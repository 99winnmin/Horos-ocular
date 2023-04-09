import re
from pprint import pprint
from urllib import request
from ast import literal_eval
import boto3
from botocore.config import Config
from HorusOculars.mongo_db_connect import get_database


def stt(video_uri, vname):
    dbname = get_database()
    collection_name = dbname["speech_indexed_data"]

    # Transcribe를 위한 Config 설정
    my_config = Config(
        region_name='ap-northeast-2',
        signature_version='v4',
        retries={
            'max_attempts': 5,
            'mode': 'standard'
        }
    )

    # Transcribe 실행
    transcribe = boto3.client('transcribe', config=my_config)

    # s3에 업로드한 파일 URL
    # job_uri = 's3://horusocular/email@email.com/video/western.mp4'
    job_uri = video_uri

    path_string = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", job_uri)
    jn = re.search('video(.+?)mp4', path_string).group(1)

    transcribe.start_transcription_job(
        TranscriptionJobName=jn+'test',
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp4',
        LanguageCode='en-US',
    )

    # Transcribe job 작업이 끝나면 결과값 불러옴
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=jn)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            save_json_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break

    # Transcribe 결과가 저장된 웹주소
    save_json_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']

    # 웹서버 결과 파이썬으로 불러오기
    load = request.urlopen(save_json_uri)
    confirm = load.status
    rst = load.read().decode('utf-8')

    # 문자열을 딕셔너리로 변환 후 결과 가져오기
    transcribe_text = literal_eval(rst)['results']

    indexed_data = {'_id': vname, 'data': transcribe_text}

    collection_name.insert_one(indexed_data)