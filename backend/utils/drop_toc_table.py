import os
import psycopg2
from psycopg2 import sql, Error
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_TOC_DB"),
    user=os.getenv("POSTGRES_TOC_USER"),
    password=os.getenv("POSTGRES_TOC_PASSWORD"),
    host="localhost",
    port=os.getenv("POSTGRES_TOC_PORT")
)
cursor = conn.cursor()

# テーブルを完全に削除
drop_table_query = sql.SQL("DROP TABLE {} CASCADE").format(sql.Identifier('toc_table'))

try:
    cursor.execute(drop_table_query)
    conn.commit()
    print("テーブルのデータが完全に削除されました。")
except Error as e:
    if e.pgcode == '42P01':  # Undefined table
        print("エラー: テーブルは存在しません。")
    else:
        print(f"エラーが発生しました: {e}")
finally:
    cursor.close()
    conn.close()
