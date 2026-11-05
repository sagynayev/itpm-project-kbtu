import { useState } from "react";

import { askQuestion, login, register } from "./api";

function AuthForm({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const action = mode === "login" ? login : register;
      const payload = await action(form);
      localStorage.setItem("pdd-token", payload.token);
      onAuthenticated(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="intro">
        <span className="eyebrow">Проверяемый помощник</span>
        <h1>Правило должно быть не только понятным, но и проверяемым.</h1>
        <p>PDD ChatBot находит официальный пункт, объясняет его простым языком и показывает источник рядом.</p>
      </section>
      <form className="auth-card" onSubmit={submit}>
        <h2>{mode === "login" ? "Войти" : "Создать аккаунт"}</h2>
        <label>
          Имя пользователя
          <input required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </label>
        {mode === "register" && (
          <label>
            Email
            <input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </label>
        )}
        <label>
          Пароль
          <input required minLength="8" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? "Подождите…" : mode === "login" ? "Войти" : "Зарегистрироваться"}</button>
        <button className="text-button" type="button" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Нет аккаунта? Регистрация" : "Уже есть аккаунт? Войти"}
        </button>
      </form>
    </main>
  );
}

function AnswerCard({ question, answer }) {
  if (answer.status === "no_source") {
    return (
      <article className="answer-card warning">
        <span className="status">Источник не найден</span>
        <h2>{question}</h2>
        <p>{answer.explanation}</p>
      </article>
    );
  }

  return (
    <article className="answer-card">
      <span className="status">Ответ основан на найденном пункте</span>
      <h2>{question}</h2>
      <section><h3>Короткий ответ</h3><p>{answer.short_answer}</p></section>
      <section><h3>Почему</h3><p>{answer.explanation}</p></section>
      <section className="source">
        <div><h3>Официальный пункт</h3><strong>{answer.official_clause.article_number} · {answer.official_clause.title}</strong></div>
        <a href={answer.official_clause.source_url} target="_blank" rel="noreferrer">Открыть источник ↗</a>
      </section>
    </article>
  );
}

function Chat({ session, onLogout }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    const currentQuestion = question.trim();
    if (!currentQuestion) return;
    setBusy(true);
    setError("");
    try {
      const answer = await askQuestion(session.token, currentQuestion);
      setMessages((current) => [{ question: currentQuestion, answer }, ...current]);
      setQuestion("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header>
        <div className="brand"><span>PDD</span> ChatBot</div>
        <div className="user"><span>{session.username}</span><button className="text-button" onClick={onLogout}>Выйти</button></div>
      </header>
      <section className="hero">
        <span className="eyebrow">Русский · MVP</span>
        <h1>Спросите о дорожной ситуации</h1>
        <p>Система ответит только тогда, когда найдёт подходящий официальный пункт.</p>
        <form className="ask-form" onSubmit={submit}>
          <textarea required rows="3" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Например: как определить приоритет на перекрёстке?" />
          <button disabled={busy}>{busy ? "Ищем пункт…" : "Найти ответ"}</button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>
      <section className="answers">
        {messages.map((message, index) => <AnswerCard key={`${message.question}-${index}`} {...message} />)}
        {!messages.length && <p className="empty">Здесь появятся ответы и ссылки на источники.</p>}
      </section>
    </main>
  );
}

export default function App() {
  const storedToken = localStorage.getItem("pdd-token");
  const [session, setSession] = useState(storedToken ? { token: storedToken, username: "Пользователь" } : null);

  function logout() {
    localStorage.removeItem("pdd-token");
    setSession(null);
  }

  return session ? <Chat session={session} onLogout={logout} /> : <AuthForm onAuthenticated={setSession} />;
}

