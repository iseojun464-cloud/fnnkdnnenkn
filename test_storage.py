import tempfile
import unittest
from pathlib import Path
from storage import SUBJECTS, init_db, add_task, list_tasks, set_completed, update_task, delete_task

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'tasks.db'
        init_db(self.db)
    def tearDown(self): self.tmp.cleanup()
    def test_eight_subjects(self): self.assertEqual(len(SUBJECTS),8)
    def test_crud_and_filters(self):
        first=add_task(self.db,'PLC','회로 결선','2026-12-01',180)
        second=add_task(self.db,'파이썬','실습','2026-11-20',30)
        self.assertEqual([t['id'] for t in list_tasks(self.db)],[second,first])
        self.assertEqual(len(list_tasks(self.db,'PLC')),1)
        self.assertEqual(set_completed(self.db,first,True),1)
        self.assertEqual(len(list_tasks(self.db,status='완료')),1)
        self.assertEqual(len(list_tasks(self.db,status='진행 중')),1)
        update_task(self.db,first,'전자기학','수정 과제','2026-11-30',60)
        self.assertEqual(list_tasks(self.db,status='완료')[0]['title'],'수정 과제')
        self.assertEqual(delete_task(self.db,second),1)
        self.assertEqual(len(list_tasks(self.db)),1)
    def test_invalid(self):
        for subject,title,minutes in [('잘못된 과목','과제',10),('PLC','  ',10),('PLC','과제',0)]:
            with self.assertRaises(ValueError): add_task(self.db,subject,title,'2026-12-01',minutes)
        with self.assertRaises(ValueError): add_task(self.db,'PLC','과제','not-a-date',30)
    def test_persistence(self):
        add_task(self.db,'된사람','주간 과제','2026-12-02',30)
        init_db(self.db)
        self.assertEqual(len(list_tasks(self.db)),1)

if __name__ == '__main__': unittest.main()
