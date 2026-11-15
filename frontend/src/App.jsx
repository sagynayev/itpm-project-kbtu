import { useEffect, useMemo, useState } from "react";

import { askQuestion, getHistory, getProfile, getPublicStats, login, register, sendFeedback, updateProfile } from "./api";

const SUGGESTIONS = [
  "Кому уступать на нерегулируемом перекрёстке?",
  "Где запрещена остановка?",
  "Когда включать аварийную сигнализацию?",
  "Что сделать перед пешеходным переходом?",
];

function Logo({ light = false }) {
  return <a className={`logo ${light ? "logo--light" : ""}`} href="#top" aria-label="PDD Check — на главную"><span>PDD</span><i>/</i>CHECK</a>;
}

function ArrowIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>;
}

function ShieldIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 4.5 6v5.5c0 4.8 3.2 8.3 7.5 9.5 4.3-1.2 7.5-4.7 7.5-9.5V6L12 3Z" /><path d="m8.7 12 2.1 2.1 4.8-5" /></svg>;
}

function ProductPreview() {
  return (
    <div className="product-preview" aria-label="Пример ответа PDD Check">
      <div className="preview-bar"><span className="preview-dot" /><span>Проверка дорожной ситуации</span><b>RU</b></div>
      <div className="preview-question"><small>Ваш вопрос</small><p>Нужно ли уступать пешеходу на нерегулируемом переходе?</p></div>
      <div className="preview-answer">
        <div className="verified-pill"><ShieldIcon /> Источник подтверждён</div>
        <h3>Да, водитель уступает дорогу пешеходу.</h3>
        <p>Ответ показывается вместе с официальной формулировкой — без догадок и скрытого источника.</p>
        <div className="preview-source"><span>ПДД РК</span><strong>Пункт 106</strong><em>ИПС «Әділет» ↗</em></div>
      </div>
    </div>
  );
}

function AuthModal({ initialMode = "register", onClose, onAuthenticated }) {
  const [mode, setMode] = useState(initialMode);
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const closeOnEscape = (event) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = await (mode === "login" ? login : register)(form);
      localStorage.setItem("pdd-token", payload.token);
      localStorage.setItem("pdd-username", payload.username);
      onAuthenticated(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="auth-modal" role="dialog" aria-modal="true" aria-labelledby="auth-title">
        <button className="modal-close" type="button" onClick={onClose} aria-label="Закрыть">×</button>
        <div className="auth-mark"><ShieldIcon /></div>
        <p className="kicker">Личный кабинет</p>
        <h2 id="auth-title">{mode === "login" ? "С возвращением" : "Начните с вопроса"}</h2>
        <p className="auth-copy">История запросов и ссылки на официальные пункты сохранятся в профиле.</p>
        <form onSubmit={submit}>
          <label>Логин<input autoFocus required autoComplete="username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
          {mode === "register" && <label>Email<input required type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>}
          <label>Пароль<input required minLength="8" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          {error && <p className="form-error">{error}</p>}
          <button className="button button--acid button--wide" disabled={busy}>{busy ? "Подключаем…" : mode === "login" ? "Войти" : "Создать аккаунт"}<ArrowIcon /></button>
        </form>
        <button className="auth-switch" type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти"}
        </button>
      </section>
    </div>
  );
}

function Landing({ onAuth }) {
  const [stats, setStats] = useState(null);
  useEffect(() => { getPublicStats().then(setStats).catch(() => null); }, []);
  const formattedDate = stats?.last_updated ? new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "long", year: "numeric" }).format(new Date(`${stats.last_updated}T00:00:00`)) : "актуальная редакция";

  return (
    <div className="landing" id="top">
      <nav className="marketing-nav">
        <Logo />
        <div className="nav-links"><a href="#how">Как работает</a><a href="#safety">Надёжность</a><a href="#about">О проекте</a></div>
        <div className="nav-actions"><button className="link-button" onClick={() => onAuth("login")}>Войти</button><button className="button button--dark" onClick={() => onAuth("register")}>Задать вопрос <ArrowIcon /></button></div>
      </nav>

      <main>
        <section className="hero-section">
          <div className="hero-copy">
            <div className="availability"><span /> ПДД РК · официальный источник</div>
            <h1>Спросите<br />как водитель.<br /><em>Проверьте</em> как юрист.</h1>
            <p>Разбираем дорожную ситуацию понятным языком и рядом показываем точный пункт действующих ПДД. Если источника нет — не додумываем.</p>
            <div className="hero-actions"><button className="button button--acid" onClick={() => onAuth("register")}>Проверить ситуацию <ArrowIcon /></button><a className="text-link" href="#how">Посмотреть принцип ↓</a></div>
            <div className="hero-proof"><span><b>{stats?.clauses ?? "—"}</b> фрагментов в базе</span><span><b>1</b> официальный источник</span><span><b>0</b> ответов без ссылки</span></div>
          </div>
          <div className="hero-visual"><div className="road-label">A13 / SAFE ROUTE</div><ProductPreview /><div className="speed-sign">106<small>пункт</small></div></div>
        </section>

        <section className="source-strip" aria-label="Данные источника"><span>Источник</span><strong>ИПС «Әділет»</strong><span>Редакция базы</span><strong>{formattedDate}</strong><span>Режим</span><strong>Official source only</strong></section>

        <section className="how-section" id="how">
          <header className="section-heading"><p className="kicker">Три шага. Никакой магии.</p><h2>От ситуации<br />до пункта правил.</h2><p>Сервис не заменяет официальный текст. Он помогает быстрее найти и понять нужное место.</p></header>
          <div className="steps-grid">
            <article><span>01</span><h3>Опишите ситуацию</h3><p>Пишите своими словами: перекрёсток, парковка, обгон или пешеход.</p></article>
            <article><span>02</span><h3>Получите ориентир</h3><p>Покажем короткий ответ и раздел, к которому относится вопрос.</p></article>
            <article><span>03</span><h3>Откройте источник</h3><p>Официальная формулировка и ссылка на «Әділет» всегда рядом.</p></article>
          </div>
        </section>

        <section className="safety-section" id="safety">
          <div className="safety-lead"><p className="kicker">Safety by design</p><h2>Лучше честное «не найдено», чем уверенная ошибка.</h2></div>
          <div className="safety-grid">
            <article className="safety-card safety-card--acid"><ShieldIcon /><h3>Guardrail проверяет связь ответа с найденным пунктом</h3><p>Нет подтверждаемой формулировки или доверенного домена — ответ блокируется.</p></article>
            <article className="safety-card"><span className="metric">SOURCE</span><h3>Единая точка истины</h3><p>Приказ МВД РК №534 в официальной информационно-правовой системе.</p></article>
            <article className="safety-card"><span className="metric">LIVE</span><h3>Обновляемая база</h3><p>Импорт воспроизводим: дата редакции, hash и ссылка сохраняются у каждого пункта.</p></article>
            <article className="safety-card safety-card--outline"><span className="metric">RU</span><h3>Без канцелярита в навигации</h3><p>Интерфейс помогает сориентироваться, а юридический текст остаётся без изменений.</p></article>
          </div>
        </section>

        <section className="about-section" id="about"><div><p className="kicker">Учебный продукт · KBTU</p><h2>PDD Check — не экзаменационный тренажёр. Это быстрый вход в официальные правила.</h2></div><div className="about-copy"><p>Проект команды Group 14: Nurdos ведёт продукт и QA, Alikhan отвечает за платформу, Alimzhan — за retrieval, guardrail и оценку качества.</p><button className="button button--light" onClick={() => onAuth("register")}>Открыть кабинет <ArrowIcon /></button></div></section>
      </main>

      <footer><Logo light /><p>Помощник для обучения. В спорной или опасной ситуации сверяйтесь с официальным текстом и компетентными органами.</p><a href="https://old.adilet.zan.kz/rus/docs/V2300033003" target="_blank" rel="noreferrer">Официальные ПДД ↗</a></footer>
    </div>
  );
}

function AnswerView({ item, token }) {
  const [sourceOpen, setSourceOpen] = useState(false);
  const [rated, setRated] = useState(null);
  const { answer, question } = item;
  async function rate(helpful) { setRated(helpful); try { await sendFeedback(token, answer.id, helpful); } catch { setRated(null); } }

  if (answer.status === "no_source") return <article className="result result--empty"><div className="result-status result-status--warn">Источник не найден</div><h2>{question}</h2><p>{answer.explanation}</p><small>Попробуйте указать дорожный объект, манёвр и участников ситуации.</small></article>;
  if (answer.status === "blocked") return <article className="result result--empty"><div className="result-status result-status--danger">Ответ заблокирован</div><h2>{question}</h2><p>{answer.explanation}</p></article>;

  return (
    <article className="result">
      <div className="result-meta"><span className="result-status"><ShieldIcon /> Проверено источником</span><span>Совпадение {Math.round(answer.retrieval_score * 100)}%</span></div>
      <p className="question-label">Ваш вопрос</p><h2>{question}</h2>
      <div className="answer-block"><span>Коротко</span><p>{answer.short_answer}</p></div>
      <div className="answer-block answer-block--muted"><span>Контекст</span><p>{answer.explanation}</p></div>
      <button className="source-toggle" type="button" onClick={() => setSourceOpen(!sourceOpen)}><div><small>Официальный пункт</small><strong>Пункт {answer.official_clause.article_number} · {answer.official_clause.title}</strong></div><span>{sourceOpen ? "−" : "+"}</span></button>
      {sourceOpen && <div className="source-text"><p>{answer.official_clause.text}</p><a href={answer.official_clause.source_url} target="_blank" rel="noreferrer">Открыть в ИПС «Әділет» <ArrowIcon /></a><small>Редакция источника: {answer.official_clause.last_updated}</small></div>}
      <div className="result-footer"><span>Ответ был полезен?</span><button className={rated === true ? "active" : ""} onClick={() => rate(true)}>Да</button><button className={rated === false ? "active" : ""} onClick={() => rate(false)}>Нет</button></div>
    </article>
  );
}

function ProfilePanel({ profile, onSave }) {
  const [draft, setDraft] = useState(profile);
  const [saved, setSaved] = useState(false);
  useEffect(() => setDraft(profile), [profile]);
  async function submit(event) { event.preventDefault(); await onSave(draft); setSaved(true); setTimeout(() => setSaved(false), 1800); }
  return (
    <section className="profile-panel"><p className="kicker">Настройки ответа</p><h1>Ваш профиль</h1><p>Уровень и дата экзамена помогают держать контекст обучения. Официальный текст не меняется.</p><form onSubmit={submit}><div className="profile-grid"><label>Как к вам обращаться<input value={draft.display_name || ""} onChange={(e) => setDraft({ ...draft, display_name: e.target.value })} placeholder="Имя" /></label><label>Логин<input value={draft.username || ""} disabled /></label></div><div className="profile-grid"><label>Опыт<select value={draft.experience_level || "novice"} onChange={(e) => setDraft({ ...draft, experience_level: e.target.value })}><option value="novice">Начинающий</option><option value="intermediate">Продолжающий</option><option value="experienced">Опытный водитель</option></select></label><label>Дата экзамена<input type="date" value={draft.exam_date || ""} onChange={(e) => setDraft({ ...draft, exam_date: e.target.value || null })} /></label></div><button className="button button--dark">{saved ? "Сохранено ✓" : "Сохранить профиль"}</button></form></section>
  );
}

function Workspace({ session, onLogout }) {
  const [view, setView] = useState("chat");
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [activeItem, setActiveItem] = useState(null);
  const [profile, setProfile] = useState({ username: session.username, experience_level: "novice" });
  const [stats, setStats] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getHistory(session.token), getProfile(session.token), getPublicStats()]).then(([items, userProfile, publicStats]) => {
      setHistory(items); setProfile(userProfile); setStats(publicStats);
      if (items[0]?.answer) setActiveItem({ question: items[0].text, answer: items[0].answer });
    }).catch((loadError) => setError(loadError.message));
  }, [session.token]);

  const name = profile.display_name || profile.username || session.username;
  const initials = useMemo(() => name.slice(0, 2).toUpperCase(), [name]);

  async function submit(event) {
    event?.preventDefault();
    const current = question.trim();
    if (!current || busy) return;
    setBusy(true); setError(""); setView("chat");
    try {
      const answer = await askQuestion(session.token, current);
      const item = { question: current, answer };
      setActiveItem(item); setHistory((items) => [{ id: Date.now(), text: current, answer, created_at: new Date().toISOString() }, ...items]); setQuestion("");
    } catch (requestError) { setError(requestError.message); } finally { setBusy(false); }
  }

  function useSuggestion(value) { setQuestion(value); setTimeout(() => document.querySelector(".composer textarea")?.focus(), 0); }
  async function saveProfile(nextProfile) { setProfile(await updateProfile(session.token, nextProfile)); }

  return (
    <div className="workspace">
      <aside className="sidebar"><Logo light /><button className="new-chat" onClick={() => { setView("chat"); setActiveItem(null); }}><span>＋</span> Новый вопрос</button><div className="side-section"><small>Последние вопросы</small>{history.slice(0, 8).map((item) => <button key={item.id} className="history-item" onClick={() => { setView("chat"); setActiveItem({ question: item.text, answer: item.answer }); }}><span>{item.answer?.status === "answered" ? "●" : "○"}</span>{item.text}</button>)}{!history.length && <p className="side-empty">История пока пустая</p>}</div><div className="sidebar-bottom"><button className="profile-link" onClick={() => setView("profile")}><span className="avatar">{initials}</span><span><b>{name}</b><small>Профиль</small></span><em>›</em></button><button className="logout" onClick={onLogout}>Выйти</button></div></aside>

      <main className="workspace-main">
        <header className="app-header"><div><span className="live-dot" /> База ПДД РК <b>{stats?.last_updated || "подключается"}</b></div><a href={stats?.source_url || "https://old.adilet.zan.kz/rus/docs/V2300033003"} target="_blank" rel="noreferrer">Официальный источник ↗</a></header>
        {view === "profile" ? <ProfilePanel profile={profile} onSave={saveProfile} /> : <div className="chat-area">{!activeItem && <section className="chat-welcome"><p className="kicker">PDD / CHECK</p><h1>Какая ситуация<br />на дороге?</h1><p>Опишите её своими словами. Ответ появится только при наличии подходящего официального пункта.</p><div className="suggestions">{SUGGESTIONS.map((item) => <button key={item} onClick={() => useSuggestion(item)}>{item}<ArrowIcon /></button>)}</div></section>}{activeItem && <AnswerView item={activeItem} token={session.token} />}{error && <p className="workspace-error">{error}</p>}<form className="composer" onSubmit={submit}><textarea rows="2" required value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }} placeholder="Напишите вопрос о дорожной ситуации…" /><button aria-label="Отправить" disabled={busy || !question.trim()}>{busy ? <span className="spinner" /> : <ArrowIcon />}</button><small>Enter — отправить · Shift + Enter — новая строка</small></form></div>}
      </main>
    </div>
  );
}

export default function App() {
  const token = localStorage.getItem("pdd-token");
  const [session, setSession] = useState(token ? { token, username: localStorage.getItem("pdd-username") || "Пользователь" } : null);
  const [authMode, setAuthMode] = useState(null);
  function logout() { localStorage.removeItem("pdd-token"); localStorage.removeItem("pdd-username"); setSession(null); }
  return <>{session ? <Workspace session={session} onLogout={logout} /> : <Landing onAuth={setAuthMode} />}{authMode && !session && <AuthModal initialMode={authMode} onClose={() => setAuthMode(null)} onAuthenticated={(payload) => { setSession(payload); setAuthMode(null); }} />}</>;
}
