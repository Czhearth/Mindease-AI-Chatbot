const chatMessages = document.getElementById("chatMessages")
const input = document.getElementById("messageInput")
const sendBtn = document.getElementById("sendBtn")
const themeToggle = document.getElementById("themeToggle")
const welcomeScreen = document.getElementById("welcomeScreen")
const homeBtn = document.getElementById("homeBtn")
const logoBtn = document.getElementById("logoBtn")
const toolBtn = document.getElementById("toolBtn")
const popup = document.getElementById("exercisePopup")

let sessionId = null
let moodAsked = false
let isBotTyping = false

/* 🔥 YOUR BACKEND URL */
const API_URL = "https://mindease-ai-chatbot-zyts.onrender.com"

/* =========================
   ADD MESSAGE
========================= */

function addMessage(text, type){

const bubble = document.createElement("div")

bubble.classList.add("message")

if(type === "user"){
bubble.classList.add("user-message")
}else{
bubble.classList.add("ai-message")
}

bubble.innerText = text

chatMessages.appendChild(bubble)
chatMessages.scrollTop = chatMessages.scrollHeight

}

/* =========================
   SEND BUTTON CONTROL
========================= */

function setSendState(disabled){

sendBtn.disabled = disabled

if(disabled){
sendBtn.style.opacity = "0.5"
sendBtn.style.cursor = "not-allowed"
}else{
sendBtn.style.opacity = "1"
sendBtn.style.cursor = "pointer"
}

}

/* =========================
   CRISIS SUPPORT
========================= */

function showCrisisSupport(){

const container = document.createElement("div")
container.classList.add("message","ai-message")

container.style.background = "#7f1d1d"
container.style.color = "white"

container.innerHTML = `
<div style="font-weight:600;margin-bottom:8px;">
You’re not alone 🤍
</div>
<div style="font-size:14px;margin-bottom:10px;">
If you're feeling overwhelmed, talking to someone can help.
</div>
<button id="helplineBtn" style="
padding:8px 12px;
border:none;
border-radius:8px;
background:white;
color:#7f1d1d;
cursor:pointer;
">📞 Find Helpline</button>
`

chatMessages.appendChild(container)
chatMessages.scrollTop = chatMessages.scrollHeight

document.getElementById("helplineBtn").onclick = ()=>{
window.open("https://findahelpline.com/", "_blank")
}

}

/* =========================
   MOOD BUTTONS
========================= */

function addMoodButtons(){

const container = document.createElement("div")
container.classList.add("message","ai-message")

const moods = [
{label:"😊 Happy", value:"happy"},
{label:"😐 Neutral", value:"neutral"},
{label:"😔 Sad", value:"sad"},
{label:"😰 Anxious", value:"anxious"}
]

moods.forEach(mood=>{
const btn = document.createElement("button")
btn.innerText = mood.label

btn.style.margin = "5px"
btn.style.padding = "8px 14px"
btn.style.borderRadius = "12px"
btn.style.border = "none"
btn.style.cursor = "pointer"
btn.style.background = "#E2E8F0"

btn.onclick = ()=>{
logMood(mood.value)
container.remove()
}

container.appendChild(btn)
})

chatMessages.appendChild(container)
chatMessages.scrollTop = chatMessages.scrollHeight

}

/* =========================
   SEND MESSAGE
========================= */

async function sendMessage(){

if(isBotTyping) return

const text = input.value.trim()
if(!text) return

if(welcomeScreen){
welcomeScreen.style.display = "none"
}

addMessage(text, "user")
input.value = ""

isBotTyping = true
setSendState(true)

/* typing bubble */
const typingBubble = document.createElement("div")
typingBubble.classList.add("message","ai-message")
typingBubble.innerText = "..."
chatMessages.appendChild(typingBubble)

chatMessages.scrollTop = chatMessages.scrollHeight

try{

const res = await fetch(`${API_URL}/chat`,{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
message:text,
session_id:sessionId
})
})

const data = await res.json()
sessionId = data.session_id

typingBubble.remove()

addMessage(data.reply, "ai")

/* crisis */
if(data.reply && (data.reply.includes("not alone") || data.reply.includes("immediate danger"))){
showCrisisSupport()
isBotTyping = false
setSendState(false)
return
}

/* mood once */
if(!moodAsked){
moodAsked = true
setTimeout(()=>addMoodButtons(), 1000)
}

}catch{

typingBubble.remove()
addMessage("Server connection error", "ai")

}

isBotTyping = false
setSendState(false)

}

/* =========================
   EVENTS
========================= */

sendBtn.onclick = sendMessage

input.addEventListener("keydown", (e)=>{
if(e.key === "Enter"){
if(isBotTyping){
e.preventDefault()
return
}
sendMessage()
}
})

/* =========================
   QUICK BUTTONS
========================= */

function quickMessage(text){

if(isBotTyping) return

if(welcomeScreen){
welcomeScreen.style.display = "none"
}

input.value = text
sendMessage()

}

/* =========================
   DARK MODE
========================= */

themeToggle.onclick = () => {

document.body.classList.toggle("dark")

if(document.body.classList.contains("dark")){
localStorage.setItem("theme", "dark")
}else{
localStorage.setItem("theme", "light")
}

}

window.onload = () => {

const savedTheme = localStorage.getItem("theme")

if(savedTheme === "dark"){
document.body.classList.add("dark")
}

}

/* =========================
   HOME BUTTON
========================= */

function goHome(){

chatMessages.innerHTML = ""
sessionId = null
moodAsked = false
isBotTyping = false

if(welcomeScreen){
welcomeScreen.style.display = "block"
}

input.value = ""
setSendState(false)

}

homeBtn.onclick = goHome
logoBtn.onclick = goHome

/* =========================
   EXERCISE POPUP
========================= */

toolBtn.onclick = (e) => {
e.stopPropagation()
popup.style.display =
popup.style.display === "block" ? "none" : "block"
}

document.addEventListener("click", (e)=>{
if(!popup.contains(e.target) && e.target !== toolBtn){
popup.style.display = "none"
}
})

/* =========================
   EXERCISES
========================= */

function breathingExercise(){

popup.style.display = "none"

addMessage("Let’s take a slow breath together.", "ai")

setTimeout(()=>addMessage("Inhale… 4 seconds", "ai"), 1000)
setTimeout(()=>addMessage("Hold…", "ai"), 5000)
setTimeout(()=>addMessage("Exhale slowly…", "ai"), 9000)

}

function groundingExercise(){

popup.style.display = "none"

addMessage("Let’s slow things down together 🌿", "ai")

setTimeout(()=>addMessage("Name 5 things you can see 👀", "ai"), 1500)
setTimeout(()=>addMessage("Take your time…", "ai"), 5000)
setTimeout(()=>addMessage("Now 4 things you can feel ✋", "ai"), 9000)

}

function gratitudeExercise(){

popup.style.display = "none"

addMessage("Tell me 3 things you're grateful for today 💙", "ai")

}

/* =========================
   MOOD LOGGING
========================= */

async function logMood(mood){

addMessage(`Got it. You're feeling ${mood}.`, "ai")

setTimeout(()=>{
addMessage("Thanks for sharing that. Want to tell me more?", "ai")
}, 1000)

try{
await fetch(`${API_URL}/mood`,{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
session_id:sessionId,
mood:mood
})
})
}catch{}

}