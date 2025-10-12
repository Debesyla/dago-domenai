import psycopg2
import json
from psycopg2.extras import RealDictCursor
from config import get_db_connect_kwargs

def main():
    conn = psycopg2.connect(**get_db_connect_kwargs())
    cur = conn.cursor()

    # ensure domain exists
    cur.execute("INSERT INTO domains (domain_name) VALUES (%s) ON CONFLICT (domain_name) DO NOTHING RETURNING id;", ("test.lt",))
    if cur.rowcount == 1:
        domain_id = cur.fetchone()[0]
    else:
        cur.execute("SELECT id FROM domains WHERE domain_name = %s", ("test.lt",))
        domain_id = cur.fetchone()[0]

    # find check_status task id
    cur.execute("SELECT id FROM tasks WHERE name = %s", ("check_status",))
    task_row = cur.fetchone()
    if not task_row:
        raise SystemExit("Task 'check_status' not found in tasks table")
    task_id = task_row[0]

    # insert a fake result (JSONB)
    payload = {"code": 200, "redirect": False, "final_url": "https://test.lt/"}
    cur.execute("""
        INSERT INTO results (domain_id, task_id, status, data)
        VALUES (%s, %s, %s, %s) RETURNING id, checked_at
    """, (domain_id, task_id, "success", json.dumps(payload)))

    res_id, checked_at = cur.fetchone()
    conn.commit()

    print("Inserted result id:", res_id)
    print("checked_at:", checked_at)

    # show the inserted row
    cur2 = conn.cursor(cursor_factory=RealDictCursor)
    cur2.execute("SELECT r.id, d.domain_name, t.name as task, r.status, r.data, r.checked_at FROM results r JOIN domains d ON d.id=r.domain_id JOIN tasks t ON t.id=r.task_id WHERE r.id=%s", (res_id,))
    row = cur2.fetchone()
    print("Row:", json.dumps(row, default=str, indent=2))

    cur2.close()
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
