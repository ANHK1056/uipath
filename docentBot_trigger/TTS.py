from gtts import gTTS
from google.cloud import storage
from google.oauth2 import service_account
import io
import uuid
import cx_Oracle

def TTS(user_id):
    credentials = service_account.Credentials.from_service_account_file("C:\\dev\\uipath\\docentBot_trigger\\axial-sight-405100-8430d171fe67.json")
    client = storage.Client(credentials=credentials)
    bucket = client.get_bucket("dobot-storage")

    cx_Oracle.init_oracle_client(config_dir=r"C:\dev\Wallet_edudb")
    con = cx_Oracle.connect(user=user_id, password="kosa2023oraclE", dsn="edudb_high")
    cur = con.cursor()
   
    sql_select = """
            SELECT p.description, u.email, p.audio, p.id
            FROM PAINTINGS p 
            JOIN USERS u
            ON p.users_id = u.id
            WHERE p.audio IS NOT NULL and p.res_time IS NULL
            """
    cur.execute(sql_select)
    results = cur.fetchall()
    email_id = []
    if results:
        for result in results:
            my_text = str(result[0])
            language = 'ko'
            myobj = gTTS(text=my_text, lang=language, slow=False)
            audio = str(result[2])
            audio_buffer = io.BytesIO()
            myobj.write_to_fp(audio_buffer)
            audio_buffer.seek(0) 

            blob = bucket.blob("audio/" + audio)
            blob.upload_from_file(audio_buffer, content_type='audio/mp3')
            p_id = str(result[3])
            email_id.append((str(result[1]),p_id))
            # myobj.save(f"{audiopath}{audio}")
            sql = """
            BEGIN
            UPDATE paintings
            SET
            res_time = current_date
            WHERE id = :p_id;
            COMMIT;
            END;
            """
            cur.execute(sql,[p_id])
    
    con.commit() # 커밋을 수행하여 변경 내용을 데이터베이스에 반영
    

    
    return email_id

    

if __name__ == '__main__':
  
    print(TTS("kcc21"))