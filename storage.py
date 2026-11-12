import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

SUBJECTS = ['파이썬', '전력공학', '된사람', '회로망이론', '전자회로실험', '전자기학', '직류기기', 'PLC']

@contextmanager
def connect(db_path):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(db_path):
    with connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            estimated_minutes INTEGER NOT NULL CHECK(estimated_minutes > 0),
            completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')

def add_task(db_path, subject, title, due_date, estimated_minutes):
    title = title.strip()
    if subject not in SUBJECTS: raise ValueError('올바른 과목을 선택하세요.')
    if not title: raise ValueError('과제명을 입력하세요.')
    due = date.fromisoformat(str(due_date))
    minutes = int(estimated_minutes)
    if minutes < 1: raise ValueError('예상 소요시간은 1분 이상이어야 합니다.')
    with connect(db_path) as conn:
        cur = conn.execute('INSERT INTO tasks (subject,title,due_date,estimated_minutes) VALUES (?,?,?,?)', (subject,title,due.isoformat(),minutes))
        return cur.lastrowid

def list_tasks(db_path, subject=None, status='전체'):
    clauses, args = [], []
    if subject and subject != '전체':
        clauses.append('subject=?'); args.append(subject)
    if status == '진행 중': clauses.append('completed=0')
    elif status == '완료': clauses.append('completed=1')
    query = 'SELECT * FROM tasks' + (' WHERE ' + ' AND '.join(clauses) if clauses else '') + ' ORDER BY completed ASC, due_date ASC, id DESC'
    with connect(db_path) as conn:
        return [dict(row) for row in conn.execute(query,args).fetchall()]

def set_completed(db_path, task_id, completed):
    with connect(db_path) as conn:
        return conn.execute('UPDATE tasks SET completed=? WHERE id=?',(int(bool(completed)),task_id)).rowcount

def delete_task(db_path, task_id):
    with connect(db_path) as conn:
        return conn.execute('DELETE FROM tasks WHERE id=?',(task_id,)).rowcount

def update_task(db_path, task_id, subject, title, due_date, estimated_minutes):
    title=title.strip()
    if subject not in SUBJECTS or not title: raise ValueError('과목과 과제명을 확인하세요.')
    due=date.fromisoformat(str(due_date))
    minutes=int(estimated_minutes)
    if minutes < 1: raise ValueError('예상 소요시간은 1분 이상이어야 합니다.')
    with connect(db_path) as conn:
        return conn.execute('UPDATE tasks SET subject=?, title=?, due_date=?, estimated_minutes=? WHERE id=?',(subject,title,due.isoformat(),minutes,task_id)).rowcount
