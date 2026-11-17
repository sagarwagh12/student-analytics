let subjectChart, classChart, loggedIn = false;
const $ = id => document.getElementById(id);
async function api(path, options={}) {
  const response = await fetch(path, {headers:{"Content-Type":"application/json"}, ...options});
  const data = await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}
$("loginForm").addEventListener("submit", async e => {
  e.preventDefault(); $("loginMessage").textContent = "Signing in...";
  try {
    const result = await api("/api/login",{method:"POST",body:JSON.stringify({username:$("username").value,password:$("password").value})});
    loggedIn = true; $("loginPanel").hidden = true; $("appPanel").hidden = false;
    $("userBadge").textContent = `${result.username} · ${result.role}`;
    await loadStudents(); await refreshDashboard();
  } catch(err) {$("loginMessage").textContent = err.message;}
});
$("logoutBtn").addEventListener("click",()=>{loggedIn=false;$("appPanel").hidden=true;$("loginPanel").hidden=false;$("userBadge").textContent="Demo Project";});
async function loadStudents(){
  const students=await api("/api/students");
  $("studentId").innerHTML=students.map(s=>`<option value="${s.student_id}">${s.student_id} - ${s.name}</option>`).join("");
}
async function refreshDashboard(){
  if(!loggedIn)return;
  try{
    const [s,r]=await Promise.all([api("/api/summary"),api("/api/records")]);
    $("totalStudents").textContent=s.total_students;
    $("averageMarks").textContent=s.average_marks+"%";
    $("attendance").textContent=s.attendance_percentage+"%";
    $("passPercentage").textContent=s.pass_percentage+"%";
    drawCharts(s); drawRecords(r);
  }catch(e){console.error(e);}
}
function drawCharts(s){
  if(subjectChart)subjectChart.destroy(); if(classChart)classChart.destroy();
  subjectChart=new Chart($("subjectChart"),{type:"bar",data:{labels:s.subjects.map(x=>x.subject),datasets:[{label:"Average marks",data:s.subjects.map(x=>x.average),backgroundColor:"#2d80bd"}]},options:{responsive:true,scales:{y:{beginAtZero:true,max:100}}}});
  classChart=new Chart($("classChart"),{type:"doughnut",data:{labels:s.classes.map(x=>x.class_name),datasets:[{data:s.classes.map(x=>x.average),backgroundColor:["#2d80bd","#27a58a","#e9a23b","#8b70c9"]}]},options:{responsive:true}});
}
function drawRecords(rows){
  $("recordsBody").innerHTML=rows.map(r=>`<tr><td>${escapeHtml(r.name)} (${r.student_id})</td><td>${escapeHtml(r.subject)}</td><td>${escapeHtml(r.exam)}</td><td>${r.marks}</td><td>${r.attendance}%</td><td>${r.record_date}</td></tr>`).join("");
}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
$("recordForm").addEventListener("submit",async e=>{
  e.preventDefault(); $("recordMessage").textContent="Saving...";
  try{
    await api("/api/records",{method:"POST",body:JSON.stringify({
      student_id:$("studentId").value,subject:$("subject").value,exam:$("exam").value,
      marks:Number($("marks").value),attendance:Number($("attendanceInput").value)
    })});
    $("recordMessage").textContent="Record saved successfully.";
    $("recordForm").reset(); await loadStudents(); await refreshDashboard();
  }catch(err){$("recordMessage").textContent=err.message;}
});
setInterval(refreshDashboard,5000);
