from datetime import date, timedelta
from pathlib import Path
import os
import streamlit as st
from storage import SUBJECTS, init_db, add_task, list_tasks, set_completed, delete_task, update_task

st.set_page_config(page_title='대학 과제 관리', page_icon='📚', layout='wide', initial_sidebar_state='collapsed')
DB_PATH = os.environ.get('TASK_DB_PATH', str(Path(__file__).parent / 'data' / 'tasks.db'))
init_db(DB_PATH)

st.markdown('''<style>
.block-container {max-width: 1120px; padding-top: 1.5rem; padding-bottom: 3rem}
h1 {font-size: clamp(1.7rem, 4vw, 2.5rem)!important}
[data-testid="stMetric"] {background: #f5f7fb; padding: 1rem; border-radius: 14px}
@media (max-width: 640px) { .block-container {padding-left: .85rem; padding-right: .85rem} [data-testid="stHorizontalBlock"] {gap: .5rem} }
</style>''', unsafe_allow_html=True)

st.title('📚 대학 과제 관리')
st.caption('8개 과목의 과제와 마감일을 한곳에서 관리하세요. · iPad Safari 대응')
all_tasks = list_tasks(DB_PATH)
today = date.today()
remaining = [t for t in all_tasks if not t['completed']]
overdue = sum(date.fromisoformat(t['due_date']) < today for t in remaining)
due_week = sum(today <= date.fromisoformat(t['due_date']) <= today + timedelta(days=7) for t in remaining)
metrics = st.columns(3)
metrics[0].metric('진행 중', f'{len(remaining)}개')
metrics[1].metric('7일 이내 마감', f'{due_week}개')
metrics[2].metric('기한 지남', f'{overdue}개')

with st.expander('➕ 새 과제 등록', expanded=not bool(all_tasks)):
    with st.form('add_task', clear_on_submit=True):
        subject = st.selectbox('과목', SUBJECTS)
        title = st.text_input('과제명', placeholder='예: 14장 연습문제 풀기')
        col1,col2 = st.columns(2)
        due = col1.date_input('마감일', value=today + timedelta(days=3), format='YYYY-MM-DD')
        minutes = col2.number_input('예상 소요시간 (분)', min_value=1, max_value=10000, value=60, step=10)
        if st.form_submit_button('과제 추가', type='primary', use_container_width=True):
            try:
                add_task(DB_PATH, subject, title, due, minutes)
                st.rerun()
            except ValueError as e:
                st.error(str(e))

st.subheader('과제 목록')
filter1, filter2 = st.columns(2)
subject_filter = filter1.selectbox('과목 필터', ['전체'] + SUBJECTS)
status_filter = filter2.segmented_control('진행 상태', ['전체','진행 중','완료'], default='진행 중')
tasks = list_tasks(DB_PATH, subject_filter, status_filter or '진행 중')
if not tasks:
    st.info('해당 조건의 과제가 없습니다. 새 과제를 등록해 보세요.')

for task in tasks:
    due_day = date.fromisoformat(task['due_date'])
    days = (due_day - today).days
    d_label = 'D-day' if days == 0 else (f'D-{days}' if days > 0 else f'D+{-days} (기한 지남)')
    with st.container(border=True):
        top, action = st.columns([5,1], vertical_alignment='center')
        top.markdown(f"**{task['title']}**")
        top.caption(f"{task['subject']}  ·  {due_day:%Y-%m-%d} ({d_label})  ·  예상 {task['estimated_minutes']}분")
        completed = action.checkbox('완료', value=bool(task['completed']), key=f"done_{task['id']}")
        if completed != bool(task['completed']):
            set_completed(DB_PATH, task['id'], completed)
            st.rerun()
        with st.expander('수정 / 삭제'):
            with st.form(f"edit_{task['id']}"):
                new_subject = st.selectbox('과목', SUBJECTS, index=SUBJECTS.index(task['subject']), key=f"subject_{task['id']}")
                new_title = st.text_input('과제명', task['title'], key=f"title_{task['id']}")
                a,b = st.columns(2)
                new_due = a.date_input('마감일', due_day, key=f"due_{task['id']}")
                new_minutes = b.number_input('예상 소요시간 (분)', min_value=1, max_value=10000, value=task['estimated_minutes'], key=f"minutes_{task['id']}")
                if st.form_submit_button('변경사항 저장', use_container_width=True):
                    try:
                        update_task(DB_PATH, task['id'], new_subject, new_title, new_due, new_minutes)
                        st.rerun()
                    except ValueError as e: st.error(str(e))
            if st.button('이 과제 삭제', key=f"delete_{task['id']}", type='secondary'):
                delete_task(DB_PATH, task['id'])
                st.rerun()

st.divider()
st.caption('데이터는 실행 서버의 SQLite 파일에 저장됩니다. Streamlit Community Cloud 등 임시 파일 시스템에서는 재시작 시 데이터가 사라질 수 있으므로 영구 저장소가 필요합니다.')
