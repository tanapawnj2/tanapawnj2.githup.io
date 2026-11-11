// site-nav.js — แถบนำทางร่วมของทุกหน้าเครื่องมือ
//  • ซ้ายบน : ปุ่ม "← หน้าหลัก" กลับไป Main.html
//  • ขวาบน : ชื่อผู้ใช้ + ปุ่มออกจากระบบ (เฉพาะหน้าที่ยังไม่มีปุ่ม #btn-logout ของตัวเอง)
// ใช้งาน: ใส่ <script type="module" src="site-nav.js"></script> ใน <head>
import { initializeApp, getApps, getApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const HOME_PAGE  = "Main.html";
const LOGIN_PAGE = "index.html";

const firebaseConfig = {
  apiKey:            "AIzaSyBKhes9uVB7tFATNChmYJtkSGXtoV8pGoI",
  authDomain:        "civiltoolskit.firebaseapp.com",
  projectId:         "civiltoolskit",
  storageBucket:     "civiltoolskit.firebasestorage.app",
  messagingSenderId: "108662763128",
  appId:             "1:108662763128:web:864248bfaf2fd27c52878d"
};

const style = document.createElement("style");
style.textContent = `
.ctk-nav-btn{display:inline-flex;align-items:center;gap:6px;flex-shrink:0;background:transparent;
  color:inherit;border:1px solid rgba(128,128,128,.45);border-radius:6px;padding:4px 12px;
  font-family:inherit;font-size:12px;font-weight:600;line-height:1.4;text-decoration:none;
  cursor:pointer;white-space:nowrap;transition:border-color .2s,color .2s}
.ctk-nav-btn:hover{border-color:#e8d5a3;color:#e8d5a3}
.ctk-back{margin-right:4px}
.ctk-logout:hover{border-color:#f87171;color:#f87171}
.ctk-user-group{display:inline-flex;align-items:center;gap:8px;margin-left:auto;flex-shrink:0;visibility:hidden}
.ctk-user{display:inline-flex;align-items:center;gap:6px;font-size:12px;white-space:nowrap}
.ctk-user::before{content:"";width:6px;height:6px;border-radius:50%;background:#86efac}
.ctk-fixed{position:fixed;top:10px;z-index:1000;background:rgba(24,24,27,.92);color:#f4f4f5;
  padding:4px 8px;border-radius:8px}
.ctk-fixed.ctk-left{left:10px}
.ctk-fixed.ctk-right{right:10px}
@media print{.ctk-nav{display:none!important}}
`;
document.head.appendChild(style);

// หาแถวหัวของหน้า (header หรือ .hdr) ที่จัดเรียงเป็น flex
function findHeaderRow() {
  const header = document.querySelector("body header, body .hdr");
  if (!header) return null;
  if (getComputedStyle(header).display.includes("flex")) return header;
  const flexChild = [...header.children].find(el => getComputedStyle(el).display.includes("flex"));
  return flexChild || header;
}

const row = findHeaderRow();

// ── ปุ่มกลับหน้าหลัก (ซ้ายบน) ──
const back = document.createElement("a");
back.href = HOME_PAGE;
back.className = "ctk-nav ctk-nav-btn ctk-back";
back.title = "กลับไปหน้าหลัก";
back.textContent = "← หน้าหลัก";
const titleBlock = document.querySelector("body header .title-block"); // หัวแบบมีบล็อกชื่อ (Pile Capacity)
if (titleBlock) {
  back.style.marginBottom = "12px";
  titleBlock.prepend(back);
} else if (row) {
  row.prepend(back);
} else {
  back.classList.add("ctk-fixed", "ctk-left");
  document.body.appendChild(back);
}

// ── ชื่อผู้ใช้ + ออกจากระบบ (ขวาบน) — เฉพาะหน้าที่ยังไม่มีของตัวเอง ──
if (!document.getElementById("btn-logout")) {
  const group = document.createElement("div");
  group.className = "ctk-nav ctk-user-group";
  const name = document.createElement("span");
  name.className = "ctk-user";
  const logout = document.createElement("button");
  logout.type = "button";
  logout.className = "ctk-nav-btn ctk-logout";
  logout.textContent = "ออกจากระบบ";
  group.append(name, logout);
  if (row) {
    row.appendChild(group);
  } else {
    group.classList.add("ctk-fixed", "ctk-right");
    document.body.appendChild(group);
  }

  const app  = getApps().length ? getApp() : initializeApp(firebaseConfig);
  const auth = getAuth(app);

  onAuthStateChanged(auth, user => {
    if (user) {
      name.textContent = user.displayName || (user.email || "").split("@")[0];
      group.style.visibility = "visible";
    } else {
      window.location.href = LOGIN_PAGE;
    }
  });

  logout.addEventListener("click", async () => {
    localStorage.removeItem("login_time");
    await signOut(auth);
    window.location.href = LOGIN_PAGE;
  });
}
