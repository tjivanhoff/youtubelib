from googleapiclient.discovery import build
import pandas as pd
import isodate
from IPython.display import JSON
from dateutil import parser

#Data visualization
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

#NLP
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

#-- invocation example: ---------------------------------------------------------

#api_key='YOUR-API-KEY'
#
#channel_ids=['YOUR-CHANNEL-ID',
#             # More channels
#            ]
#api_service_name = "youtube"
#api_version = "v3"
#
## Get credentials and create an API client
#youtube = build(
#    api_service_name, api_version, developerKey=api_key)
#
## Write your code...
#

#---------------------------------------------------------------------------------

#-- get_channel_stats --------------------------------
#
# La funzione get_channel_stats recupera e restituisce informazioni statistiche 
# di base su uno o più canali YouTube, come il numero di iscritti, visualizzazioni 
# totali e conteggio dei video. I dati vengono raccolti tramite l'API YouTube e 
# restituiti come un DataFrame di pandas.
#
# youtube: [obj di Google API client] l'oggetto client per interagire con l'API YouTube
# channel_ids: [list di stringhe] lista degli ID dei canali di cui recuperare le statistiche

def get_channel_stats(youtube, channel_ids):
    
    all_data=[]
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()

    #loop through items
    for item in(response['items']):
        data = {'channelName': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalViews': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        
        all_data.append(data)
        
    return(pd.DataFrame(all_data))


#-- get_video_ids --------------------------------
#
# Questa funzione recupera gli ID dei video da una playlist di YouTube. 
# Si itera su tutte le pagine della playlist fino a quando non ci sono più pagine.
#
# youtube: [oggetto] istanza dell'API di YouTube per fare richieste
# playlist_id: [stringa] l'ID della playlist da cui recuperare gli ID dei video

def get_video_ids(youtube, playlist_id):
    
    video_ids = []
    flag_first=1
    next_page_token=None
    
    while next_page_token is not None or flag_first==1:

        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId="UUujcr3rSdv-m_HqdN2Nq4HQ",
            maxResults = 50
        )

        response = request.execute()
    
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
    
        flag_first=0

        next_page_token = response.get('nextPageToken')
    
        
    return video_ids


#-- get_video_details --------------------------------
#
# La funzione get_video_details estrae informazioni dettagliate su un insieme di video da YouTube
# utilizzando l'API di YouTube. La funzione itera sugli ID dei video, recuperando informazioni come
# titolo del canale, titolo del video, descrizione, tag, data di pubblicazione, conteggi delle visualizzazioni,
# conteggi dei mi piace, conteggi dei preferiti, conteggi dei commenti, durata del video, definizione e 
# presenza di sottotitoli. Le informazioni vengono raccolte in un DataFrame pandas per un'analisi più facile.
#
# youtube: [oggetto] un client API di YouTube autorizzato per effettuare richieste all'API di YouTube.
# video_ids: [lista di stringhe] un elenco di ID video di YouTube dai quali recuperare le informazioni.

def get_video_details(youtube, video_ids):

    all_video_info=[]
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        
        response = request.execute()
    
        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }

            video_info={}
            video_info['video_id']= video['id']

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v]=video[k][v]
                    except:
                        video_info[v]=None

            all_video_info.append(video_info)

    return pd.DataFrame(all_video_info)



#-- get_comments_in_videos ------------------------------
#
# Questa funzione recupera i commenti dai video di YouTube specificati. 
# Effettua una richiesta per ogni video in un elenco di ID video e raccoglie 
# tutti i commenti in un DataFrame pandas.
#
# youtube: [oggetto] istanza del client API di YouTube per effettuare richieste
# video_ids: [lista di stringhe] elenco degli ID dei video dai quali recuperare i commenti

def get_comments_in_videos(youtube,video_ids):
    all_comments=[]
    
    for video_id in video_ids:
        request=youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id
        )
        
        try:
            response=request.execute()
            comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items']]
            comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}
        except:
            #print ('The video {video_id} has no comment')
            comments_in_video_info = {'video_id': video_id, 'comments': None}
        all_comments.append(comments_in_video_info)
    
    return pd.DataFrame(all_comments)