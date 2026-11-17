# Local testing checklist

- [ ] Open `http://127.0.0.1:8000`
- [ ] Login as `teacher` / `Teacher123`
- [ ] Confirm the KPI cards show student count, average marks, attendance and pass percentage
- [ ] Confirm subject and class charts appear
- [ ] Add a record with marks and attendance between 0 and 100
- [ ] Confirm the new record appears in the table
- [ ] Confirm the dashboard KPIs refresh
- [ ] Try an unknown Student ID using the API docs; it should return an error
- [ ] Try marks above 100; validation should reject the input
- [ ] Capture screenshots without passwords or personal data
