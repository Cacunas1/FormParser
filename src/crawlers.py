from MainApp.models import *
from MainApp.wordcloudbuilder import WordCloudBuilder
from MainApp.smartsemanticparser import SmartSemanticParser
from MainApp.sentimentanalysis import SentimentAnalysis

#import datefinder
import datetime
from datetime import datetime, date
#import dateutil.parser
import json
import os
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from random import randint

import slate3k as slate #import slate to extract text fom PDFs

def getTextFromPdfUrl(commentURL):
    #1 Download PDF
    file = requests.get(commentURL, allow_redirects=True)
    print("DEBUG: PDF comment file.contents:", file.contents)

    #It's mandatory to change the location which the file is storage in order to put the code to work
    #open('/home/POC/MainProject/MainApp/media/commentPDF.pdf', 'wb').write(file.content)
    filepath = '/home/POC/MainProject/MainApp/tmp/tmpPDFComment.pdf'

    with open(filepath,'wb') as f:
        f.write(file.content)

    with open(filepath,'rb') as f:
        getTextFromPdfUrl = slate.PDF(f)
        getTextFromPdfUrl = getTextFromPdfUrl.text()
    try:
        os.remove(file)
    except:
        print("DEBUG: Temporary comment file in PDF cannot be deleted")

    return getTextFromPdfUrl

#% Common functions
def extract_summary(link, api_key, doc_id):
    link = link + api_key + '&documentId=' + doc_id + '&contentType=html'
    r = requests.get(link)
    soup = BeautifulSoup(r.content,'html.parser')

    if soup.find('pre') is None:
        if soup.text.find('OVER_RATE_LIMIT') != -1:
            return 'OVER_RATE_LIMIT'
        return ''
    else:
        doc_text = soup.find('pre').text

    doc_start = doc_text.find('SUMMARY:')
    doc_end = doc_text.find('DATES:',doc_start)
    summary_v1 = doc_text[doc_start:doc_end]
    # The if-else below clean the [[page x]] that sometimes appears in the
    # middle of the summary
    summary_v1_start = summary_v1.find('[[')
    if summary_v1_start==-1:
        return summary_v1.strip()
    else:
        summary_v1_end = summary_v1.find(']]', summary_v1_start)
        summary_v2 = summary_v1.replace(summary_v1[summary_v1_start:summary_v1_end+2], '')
        return " ".join(summary_v2.split())

def extract_regulation(link, api_key, doc_id):
    link = link + api_key + '&documentId=' + doc_id + '&contentType=html'
    r = requests.get(link)
    soup = BeautifulSoup(r.content,'html.parser')
    if soup.find('pre') is None:
        if soup.text.find('OVER_RATE_LIMIT') != -1:
            return 'OVER_RATE_LIMIT'
        #print('soup.text', soup.text)
        return ''
    else:
        print('Se supone success', soup.text[0:100])
        return soup.find('pre').text

def meetingDates(document):
    flag = 0
    last = ''
    count = 0
    i=0
    dateList = []

    for line in document.splitlines():
        #print(i )
        #print(line)
        if line == 'Dates':
            if (last[-1:] == '\n') or (last[-1:] == '.'):
                flag = 1
        if flag == 1:
            matches = datefinder.find_dates(line)
            for match in matches:
                if i==0 or i==1:
                    dateList.append(match)
                    i=i+1
        last = line

    return dateList

def getCommentSentiment(commentText):

    getPolaritySentiment = SentimentAnalysis().getPolaritySentiment(commentText)

    return getPolaritySentiment

def getCommentText(doc, api_key):

    commentText = ""

    try:
        if doc["attachments"] is not None:
            for attachment in doc["attachments"]:
                commentURL = attachment["fileFormats"][0]

                commentURL = commentURL.replace("download?", "download?api_key="+api_key)
                #commentURL = "https://api.data.gov/regulations/v3/download?api_key=n9v8Dnh0zTbYWWmbcZvqdQaj00Vw27tLixb3BRcq&documentId=FTC-2019-0073-0013&attachmentNumber=1&contentType=pdf"
                if commentURL.find("contentType=pdf") != -1:
                    print ("commentURL%%%", commentURL)

                    commentText = commentText + getTextFromPdfUrl(commentURL)
                    #commentText = "This comment is in PDF format and will be retrieved later"
                else:
                    print (" ####################### comment not in PDF format  #######################")

    except KeyError:
        print("No attachment in this comment")
        commentText = doc["comment"]["value"]

    print("commentText", commentText)

    return commentText

class Crawlers():
    @staticmethod

    def getDocs(api_key, lookbackDays=(365//8), SearchYear=False, Year=None):
        print("DEBUG: inside getDocs method")
        # API url for list of document5
        documentsListAPI = 'http://api.data.gov/regulations/v3/documents.json'
        #API url for document detail
        documentDetailAPI = 'http://api.data.gov/regulations/v3/document.json'
        # rEGULATION BASE URL
        regBaseURL = 'https://api.data.gov/regulations/v3/download?api_key='

        # Time Variables to be used in the request to the API
        if SearchYear:
            strFromDate = str(Year) + '-01-01'
            strToDate = str(Year) + '-12-31'
            dtFrom = datetime.strptime(strFromDate, "%Y-%m-%d")
            dtTo = datetime.strptime(strToDate, "%Y-%m-%d")
            dtFrom = dtFrom.strftime("%m/%d/%y")
            dtTo = dtTo.strftime("%m/%d/%y")
        else:
            strToDate = date.today()
            strFromDate = strToDate - datetime.timedelta(lookbackDays) #days
            dtFrom = strFromDate.strftime("%m/%d/%y")
            dtTo = strToDate.strftime("%m/%d/%y")


        # Params that goes to the initial request to the API
        params = {
          "api_key"   : api_key,
          #"countOnly" : 0, # 0: brings document list, 1 brings only doc count
          "pd"        : dtFrom + '-' + dtTo, # published date e.g. 01/01/19-12/31/19
          "cat"       : "BFS", # category (Banking and Financial)
          "sb"        : "postedDate", # sort by
          "so"        : "DESC", # sort order
          #"dktid"     : "USCIS-2019-0011",
          #"dct"       : 'N+PR+FR+O+SR', # document type not needed, we want to bring everything
          #"rpp"     : "100", # results per page
          #"po"      : 0 # page offset
        }

        print("DEBUG: Params that goes to the initial request to the API", params)
        #print("################################################################")

        documentListReq = requests.get(documentsListAPI, params)

        if documentListReq.status_code not in (500, 502, 504):
            documentListDict = json.loads(documentListReq.text)
            docsDF = pd.DataFrame(documentListDict["documents"])
        else:
            print("HTTP response code:", documentListReq.status_code)
            print("Website is in downtime. Waiting 5s and trying again...")
            #time.sleep(5)

        for index, docket in docsDF.iterrows():

            #List of regulations in the current docket
            updatedRegulations = []

            #List of regulations in the current docket those had new comments
            updatedCommentRegulations = []

            params = {
                    "api_key"  : api_key,
                    "dktid" : docket["docketId"]
                }

            docketDocumentsReq = requests.get(documentsListAPI, params)

            #print("Params that goes to request to the API List of regulations in the current docket", params)
            #print("################################################################")

            #Create or update docket
            newDocket = Docket.objects.update_or_create(
                            docket = docket["docketId"],
                            #version    = ,
                            title       = docket["docketTitle"],
                            agency      = docket["agencyAcronym"]
                        )

            docketDF = pd.DataFrame(json.loads(docketDocumentsReq.text)["documents"])

            # Sort by document type to have comments at the bottom after regulations
            docketDF = docketDF.sort_values(by=("documentType"))

            for docID in docketDF["documentId"]:

                params = {
                        "api_key"    : api_key,
                        "documentId" : docID
                    }

                documentDetailReq = requests.get(documentDetailAPI, params)

                #print("Params that goes to request to the API getting details of each document", params)
                #print("################################################################")

                doc = json.loads(documentDetailReq.text)

                if "error" in doc:
                    if "code" in doc["error"]:
                        while doc["error"]["code"] == "OVER_RATE_LIMIT":
                            print('##########   Regulation OVER_RATE_LIMIT   ###########')
                            time.sleep(15)
                            documentDetailReq = requests.get(documentDetailAPI, params)
                            doc = json.loads(documentDetailReq.text)

                text = extract_regulation(regBaseURL, api_key, docID)

                while text == 'OVER_RATE_LIMIT':
                    print('##########   Regulation OVER_RATE_LIMIT   ###########')
                    time.sleep(5)
                    text = extract_regulation(regBaseURL, api_key, docID)

                summary = extract_summary(regBaseURL, api_key, docID)

                while summary == 'OVER_RATE_LIMIT':
                    print('##########   Summary OVER_RATE_LIMIT   ###########')
                    time.sleep(5)
                    summary = extract_summary(regBaseURL, api_key, docID)


                docType = doc["documentType"]["value"]

                try:
                    documentPostedDate = doc["postedDate"]
                except KeyError:
                    documentPostedDate = date.today().strftime("%Y-%m-%d")
                except Exception as e:
                    print(type(e))


                if docType == "Notice":
                    dates = meetingDates(text)
                    if len(dates) >= 2:
                        newRegulation = Regulation.objects.update_or_create(
                            regulation_id = docID,
                            #version      = ,
                            name          = doc["title"]["value"],
                            text          = text,
                            summary       = summary,
                            date          = documentPostedDate,
                            #rin           = doc["rin"]["value"],
                            documentType  = docType,
                            region        = "US",
                            docket        = newDocket[0],
                            meetingdDate  = dates[0],
                            meetingdDate2 = dates[1]
                        )
                    elif len(dates) == 1:
                        newRegulation = Regulation.objects.update_or_create(
                            regulation_id = docID,
                            #version      = ,
                            name          = doc["title"]["value"],
                            text          = text,
                            summary       = summary,
                            date          = documentPostedDate,
                            documentType  = docType,
                            region        = "US",
                            docket        = newDocket[0],
                            meetingdDate  = dates[0]
                        )
                    else:
                        newRegulation = Regulation.objects.update_or_create(
                            regulation_id = docID,
                            #version      = ,
                            name          = doc["title"]["value"],
                            text          = text,
                            summary       = summary,
                            date          = documentPostedDate,
                            documentType  = docType,
                            region        = "US",
                            docket        = newDocket[0]
                        )
                elif docType in ("Rule", "Proposed Rule"):
                    newRegulation = Regulation.objects.update_or_create(
                        regulation_id = docID,
                        #version      = ,
                        name          = doc["title"]["value"],
                        text          = text,
                        summary       = summary,
                        date          = documentPostedDate,
                        #rin           = doc["rin"]["value"],
                        documentType  = docType,
                        region        = "US",
                        docket        = newDocket[0]
                    )

                    if doc["commentDueDate"] is not None:

                        newEventCommentStartDate = Regulation.objects.update_or_create(
                                regulation_id = docID + "commentStartDate",
                                name          = "Comments Start Date",
                                text          = "Comments Start Date For" + doc["title"]["value"],
                                summary       = "Comments Start Date For" + doc["title"]["value"],
                                date          = documentPostedDate,
                                documentType  = "CommentDate",
                                docket        = newDocket[0],
                                meetingDate  = doc["commentStartDate"],
                                meetingDate2 = doc["commentStartDate"]
                        )

                        newEventCommentDueDate = Regulation.objects.update_or_create(
                                regulation_id = docID + "commentDueDate",
                                name          = "Comments Due Date",
                                text          = "Comments Due Date For" + doc["title"]["value"],
                                summary       = "Comments Due Date For" + doc["title"]["value"],
                                date          = documentPostedDate,
                                documentType  = "CommentDate",
                                docket        = newDocket[0],
                                meetingDate  = doc["commentDueDate"],
                                meetingDate2 = doc["commentDueDate"]
                    )

                    #Include the regulation in a list to manipulate later
                    updatedRegulations.append(newRegulation[0])

                    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ')
                    print('updatedRegulations adding ', docID)
                    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ')
                    try:
                        #Create or link to topics
                        regulationTopics = doc["topics"]

                        #We must create an alternative logic in case no topic is returned
                        #Parsing another info returned in the API
                        for topic in regulationTopics:

                            newArea = Area.objects.update_or_create(name = topic)

                            newEntity_area = Entity_area.objects.update_or_create(
                                area = newArea[0],
                                regulation = newRegulation[0]
                            )
                    except KeyError:
                        print("No topics for this regulation")
                    except Exception as e:
                        print(type(e))

                # Document type for comments
                elif (docType == "Public Submission") and ("commentOnDoc" in doc):

                    commentedRegulation = Regulation.objects.filter(regulation_id=doc["commentOnDoc"]["documentId"])

                    if commentedRegulation.count() > 0:
                        commentedRegulation = commentedRegulation[0]

                        print("regulation found!")
                        print("commentText: ", doc["comment"])
                        print("postedDate: ", documentPostedDate)

                        polaritySentiment  = getCommentSentiment(doc["comment"]["value"])

                        commentText = getCommentText(doc, api_key)

                        newComment = Comment.objects.update_or_create(
                            regulation = commentedRegulation,
                            #comment    = doc["comment"]["value"],
                            comment    = commentText,
                            date       = documentPostedDate,
                            polarity  = polaritySentiment[0],
                            sentiment  = polaritySentiment[1],
                            submitterName = doc["submitterName"]["value"],
                            #organization = doc["organization"]["value"],
                            trackingNumber = doc["trackingNumber"]["value"],
                            title = doc["title"]["value"]
                        )[1]

                        if newComment:
                            #Include the regulation in a list to manipulate later since one comment can change the text analytics
                            #If the comment is an old one, it's not necessary
                            updatedCommentRegulations.append(commentedRegulation)
                else:
                    newRegulation = Regulation.objects.update_or_create(
                        regulation_id = docID,
                        #version      = ,
                        name          = doc["title"]["value"],
                        text          = text,
                        summary       = summary,
                        date          = documentPostedDate,
                        #rin           = doc["rin"]["value"],
                        documentType  = docType,
                        region        = "US",
                        docket        = newDocket[0]
                    )

            print('?????????????????????????????????')
            print('Generating Wordcloud and semantic for docket ', docket["docketId"])
            print('?????????????????????????????????')
            for updatedCommentRegulation in updatedCommentRegulations:

                print('#######################################')
                print('generating wordcloud for regulation', updatedCommentRegulation.regulation_id)
                print('#######################################')
                regulationText = updatedCommentRegulation.text #To be substituted by regulation comments

                #Delete previous WordClouds
                Wordcloud.objects.filter(regulation = updatedCommentRegulation).delete()

                #wordCountList = WordCloudBuilder().wordCount(regulationText)
                wordCountList = WordCloudBuilder().wordCount(str(Comment.objects.filter(regulation=updatedCommentRegulation)))


                for wordCount in wordCountList:
                    newWordCloud = Wordcloud.objects.create(
                        regulation = updatedCommentRegulation,
                        commentFlag = False,
                        word = wordCount[0],
                        count = wordCount[1])


            for updatedRegulation in updatedRegulations:
                #Delete previous TextSemantics
                TextSemantic.objects.filter(regulation = updatedRegulation).delete()

                regulationText = updatedRegulation.text #To be substituted by regulation comments

                semanticParsed = SmartSemanticParser().parse(regulationText)
                required = semanticParsed['required']
                advised = semanticParsed['advised']
                forbidden = semanticParsed['forbidden']

                print('#######################################')
                print('generating semantic for regulation', updatedRegulation.regulation_id)
                #print('##required##', semanticParsed['required'])
                #print('##advised##', semanticParsed['advised'])
                #print('##forbidden##', semanticParsed['forbidden'])
                print('#######################################')

                for item in required:
                    newTextSemantic = TextSemantic.objects.create(
                        regulation = updatedRegulation,
                        semanticType = 0,
                        text = item,
                        keyWord = "required"
                    )

                for item in advised:
                    newTextSemantic = TextSemantic.objects.create(
                        regulation = updatedRegulation,
                        semanticType = 1,
                        text = item,
                        keyWord = "advised"
                    )

                for item in forbidden:
                    newTextSemantic = TextSemantic.objects.create(
                        regulation = updatedRegulation,
                        semanticType = 2,
                        text = item,
                        keyWord = "forbidden"
                    )