import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  IconChevronLeft, IconChevronRight, IconPlus, IconBell,
  IconCheck, IconTrash, IconX, IconCalendarEvent, IconNotebook,
  IconBellRinging, IconBellOff, IconCircleDot,
} from '@tabler/icons-react';

// ============================================================
// Lunar conversion helper (uses lunar-javascript)
// ============================================================
let Solar, Lunar;
try {
  const pkg = require('lunar-javascript');
  Solar = pkg.Solar;
  Lunar = pkg.Lunar;
} catch (e) {
  Solar = null;
  Lunar = null;
}

function toSolar(y, m, d) {
  try { return Solar ? Solar.fromYmd(y, m, d) : null; } catch { return null; }
}

function getLunarFromSolar(y, m, d) {
  try {
    if (!Solar) return null;
    const solar = Solar.fromYmd(y, m, d);
    return solar.getLunar();
  } catch { return null; }
}

// ============================================================
// LocalStorage helpers
// ============================================================
const LS_KEY = 'calendar_notes_v2';
function loadNotes() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); } catch { return {}; }
}
function saveNotes(data) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(data)); } catch {}
}
function dayKey(y, m, d) {
  return `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
}

// ============================================================
// Reminder / Notification helpers
// ============================================================
function requestNotifPermission() {
  if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}
function sendBrowserNotif(title, body) {
  if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
    new Notification(title, { body, icon: '/logo.png' });
  }
}
function checkDueReminders(notes) {
  const now = new Date();
  const todayKey = dayKey(now.getFullYear(), now.getMonth() + 1, now.getDate());
  const dayNotes = notes[todayKey] || {};
  const reminders = dayNotes.reminders || [];
  reminders.forEach((r) => {
    if (!r.done && !r.notified) {
      sendBrowserNotif('📅 Nhắc lịch hôm nay', r.title);
      r.notified = true;
    }
  });
}

// ============================================================
// Vietnamese month/weekday names
// ============================================================
const WEEKDAYS = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
const CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];

function getDaysInMonth(y, m) {
  return new Date(y, m, 0).getDate();
}
function getFirstDayOfMonth(y, m) {
  return new Date(y, m - 1, 1).getDay(); // 0=Sun
}

// ============================================================
// NoteModal — modal ghi chú / đặt lịch
// ============================================================
function NoteModal({ dateKey, dateLabel, onClose, notes, onSave }) {
  const dayNotes = notes[dateKey] || {};
  const [tab, setTab] = useState('diary'); // diary | note | reminder
  const [diary, setDiary] = useState(dayNotes.diary || '');
  const [diaryDone, setDiaryDone] = useState(dayNotes.diaryDone || false);
  const [noteText, setNoteText] = useState(dayNotes.note || '');
  const [reminders, setReminders] = useState(dayNotes.reminders || []);
  const [newRemTitle, setNewRemTitle] = useState('');
  const [newRemRepeat, setNewRemRepeat] = useState('none'); // none|daily|3days|weekly
  const [newRemTime, setNewRemTime] = useState('08:00');

  const handleSave = () => {
    const updated = {
      ...notes,
      [dateKey]: { diary, diaryDone, note: noteText, reminders },
    };
    onSave(updated);
    onClose();
  };

  const addReminder = () => {
    if (!newRemTitle.trim()) return;
    const rem = {
      id: Date.now(),
      title: newRemTitle.trim(),
      repeat: newRemRepeat,
      time: newRemTime,
      done: false,
      notified: false,
    };
    setReminders((prev) => [...prev, rem]);
    setNewRemTitle('');
  };

  const toggleReminderDone = (id) => {
    setReminders((prev) => prev.map((r) => r.id === id ? { ...r, done: !r.done } : r));
  };
  const deleteReminder = (id) => {
    setReminders((prev) => prev.filter((r) => r.id !== id));
  };

  const REPEAT_LABELS = { none: 'Không lặp', daily: 'Mỗi ngày', '3days': 'Mỗi 3 ngày', weekly: 'Mỗi tuần' };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div
        className="relative w-full max-w-md rounded-2xl shadow-2xl overflow-hidden"
        style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}
      >
        {/* Header */}
        <div className="px-5 pt-5 pb-3 border-b" style={{ borderColor: 'var(--color-surface-border)' }}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-body font-bold text-base" style={{ color: 'var(--color-primary)' }}>
                📅 {dateLabel}
              </h3>
              <p className="text-xs font-body mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
                Ghi chú & đặt lịch nhắc
              </p>
            </div>
            <button type="button" onClick={onClose}
              className="p-1.5 rounded-lg transition-colors"
              style={{ color: 'var(--color-text-secondary)' }}>
              <IconX size={18} />
            </button>
          </div>
          {/* Tabs */}
          <div className="flex gap-1 mt-3">
            {[
              { id: 'diary', label: 'Nhật ký', icon: IconNotebook },
              { id: 'note', label: 'Ghi chú', icon: IconCalendarEvent },
              { id: 'reminder', label: 'Đặt lịch', icon: IconBellRinging },
            ].map(({ id, label, icon: Icon }) => (
              <button key={id} type="button" onClick={() => setTab(id)}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-body font-medium transition-all"
                style={{
                  background: tab === id ? 'var(--color-primary)' : 'transparent',
                  color: tab === id ? 'var(--color-text-on-primary)' : 'var(--color-text-secondary)',
                }}
              >
                <Icon size={13} />{label}
              </button>
            ))}
          </div>
        </div>

        {/* Body */}
        <div className="p-5 space-y-3 max-h-[420px] overflow-y-auto">
          {tab === 'diary' && (
            <div className="space-y-3">
              <textarea
                rows={5} value={diary} onChange={(e) => setDiary(e.target.value)}
                placeholder="Ghi lại những gì bạn đã làm hôm nay..."
                className="w-full resize-none rounded-xl border px-3.5 py-2.5 text-sm font-body outline-none transition-colors"
                style={{
                  background: 'var(--color-background)',
                  border: '1px solid var(--color-surface-border)',
                  color: 'var(--color-text-primary)',
                }}
              />
              <button
                type="button"
                onClick={() => setDiaryDone(!diaryDone)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-body font-medium transition-all w-full justify-center"
                style={{
                  background: diaryDone ? 'rgba(107,43,31,0.1)' : 'var(--color-primary)',
                  color: diaryDone ? 'var(--color-primary)' : 'var(--color-text-on-primary)',
                  border: diaryDone ? '1px solid var(--color-primary)' : 'none',
                }}
              >
                {diaryDone ? <><IconCircleDot size={16} /> Đã hoàn thành hôm nay</> : <><IconCheck size={16} /> Đánh dấu Hoàn thành</>}
              </button>
              {diaryDone && (
                <p className="text-xs text-center font-body" style={{ color: 'var(--color-text-secondary)' }}>
                  ✅ Tốt lắm! Hệ thống đã ghi nhận bạn hoàn thành ngày này.
                </p>
              )}
            </div>
          )}

          {tab === 'note' && (
            <textarea
              rows={7} value={noteText} onChange={(e) => setNoteText(e.target.value)}
              placeholder="Ghi chú nhắc nhở, kế hoạch, hoặc ý tưởng cho ngày này..."
              className="w-full resize-none rounded-xl border px-3.5 py-2.5 text-sm font-body outline-none"
              style={{
                background: 'var(--color-background)',
                border: '1px solid var(--color-surface-border)',
                color: 'var(--color-text-primary)',
              }}
            />
          )}

          {tab === 'reminder' && (
            <div className="space-y-4">
              {/* Add new reminder */}
              <div className="p-3 rounded-xl space-y-2" style={{ background: 'var(--color-background)', border: '1px solid var(--color-surface-border)' }}>
                <p className="text-xs font-body font-semibold" style={{ color: 'var(--color-text-secondary)' }}>Thêm lịch nhắc mới</p>
                <input
                  type="text" value={newRemTitle} onChange={(e) => setNewRemTitle(e.target.value)}
                  placeholder="Tiêu đề nhắc lịch..."
                  className="w-full rounded-lg border px-3 py-2 text-sm font-body outline-none"
                  style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-primary)', background: 'var(--color-surface)' }}
                />
                <div className="flex gap-2">
                  <select value={newRemRepeat} onChange={(e) => setNewRemRepeat(e.target.value)}
                    className="flex-1 rounded-lg border px-2 py-2 text-xs font-body outline-none"
                    style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-primary)', background: 'var(--color-surface)' }}>
                    {Object.entries(REPEAT_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                  </select>
                  <input type="time" value={newRemTime} onChange={(e) => setNewRemTime(e.target.value)}
                    className="rounded-lg border px-2 py-2 text-xs font-body outline-none"
                    style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-primary)', background: 'var(--color-surface)' }}
                  />
                </div>
                <button type="button" onClick={addReminder}
                  className="w-full py-2 rounded-lg text-xs font-body font-medium flex items-center justify-center gap-1.5 transition-colors"
                  style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
                  <IconPlus size={14} /> Thêm lịch
                </button>
              </div>
              {/* List reminders */}
              {reminders.length === 0 && (
                <p className="text-xs text-center py-4 font-body" style={{ color: 'var(--color-text-secondary)' }}>Chưa có lịch nhắc nào</p>
              )}
              {reminders.map((r) => (
                <div key={r.id} className="flex items-center gap-2 p-2.5 rounded-xl"
                  style={{ background: r.done ? 'rgba(107,43,31,0.06)' : 'var(--color-background)', border: '1px solid var(--color-surface-border)' }}>
                  <button type="button" onClick={() => toggleReminderDone(r.id)}
                    className="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center transition-colors"
                    style={{ background: r.done ? 'var(--color-primary)' : 'transparent', border: '2px solid var(--color-primary)' }}>
                    {r.done && <IconCheck size={12} style={{ color: 'var(--color-text-on-primary)' }} />}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-body font-medium truncate" style={{ color: 'var(--color-text-primary)', textDecoration: r.done ? 'line-through' : 'none' }}>{r.title}</p>
                    <p className="text-[10px] font-body" style={{ color: 'var(--color-text-secondary)' }}>
                      {REPEAT_LABELS[r.repeat]} • {r.time}
                    </p>
                  </div>
                  <button type="button" onClick={() => deleteReminder(r.id)}
                    className="p-1 rounded transition-colors" style={{ color: 'var(--color-text-secondary)' }}>
                    <IconTrash size={13} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 pb-5 pt-2 border-t flex gap-2" style={{ borderColor: 'var(--color-surface-border)' }}>
          <button type="button" onClick={onClose}
            className="flex-1 py-2.5 rounded-xl text-sm font-body font-medium transition-colors"
            style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-secondary)' }}>
            Hủy
          </button>
          <button type="button" onClick={handleSave}
            className="flex-1 py-2.5 rounded-xl text-sm font-body font-medium transition-colors"
            style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
            Lưu lại
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// NotificationPanel — drawer thông báo
// ============================================================
function NotificationPanel({ notes, onClose }) {
  const allReminders = [];
  Object.entries(notes).forEach(([key, val]) => {
    (val.reminders || []).forEach((r) => {
      allReminders.push({ ...r, dateKey: key });
    });
    if (val.diaryDone) {
      allReminders.push({ id: `done-${key}`, title: `Hoàn thành: ${key}`, done: true, dateKey: key, _isDone: true });
    }
  });
  allReminders.sort((a, b) => b.dateKey.localeCompare(a.dateKey));

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div
        className="relative w-80 h-full flex flex-col shadow-2xl"
        style={{ background: 'var(--color-surface)', borderLeft: '1px solid var(--color-surface-border)' }}
      >
        <div className="px-4 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--color-surface-border)' }}>
          <h3 className="font-body font-bold text-sm" style={{ color: 'var(--color-primary)' }}>
            🔔 Thông Báo & Lịch Sử
          </h3>
          <button type="button" onClick={onClose} style={{ color: 'var(--color-text-secondary)' }}>
            <IconX size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {allReminders.length === 0 && (
            <p className="text-center py-12 text-sm font-body" style={{ color: 'var(--color-text-secondary)' }}>
              Chưa có thông báo nào
            </p>
          )}
          {allReminders.map((r) => (
            <div key={`${r.dateKey}-${r.id}`} className="p-3 rounded-xl flex items-start gap-2"
              style={{ background: 'var(--color-background)', border: '1px solid var(--color-surface-border)' }}>
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ background: r._isDone ? 'rgba(107,43,31,0.15)' : r.done ? 'rgba(107,43,31,0.1)' : 'var(--color-primary)' }}>
                {r._isDone
                  ? <IconCircleDot size={14} style={{ color: 'var(--color-primary)' }} />
                  : r.done
                    ? <IconCheck size={14} style={{ color: 'var(--color-primary)' }} />
                    : <IconBell size={13} style={{ color: 'var(--color-text-on-primary)' }} />
                }
              </div>
              <div className="min-w-0">
                <p className="text-xs font-body font-medium" style={{ color: 'var(--color-text-primary)', textDecoration: r.done && !r._isDone ? 'line-through' : 'none' }}>
                  {r.title}
                </p>
                <p className="text-[10px] font-body" style={{ color: 'var(--color-text-secondary)' }}>
                  {r.dateKey} {r.time ? `• ${r.time}` : ''} {r.repeat && r.repeat !== 'none' ? `• lặp` : ''}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Main CalendarView Component
// ============================================================
export default function CalendarView() {
  const today = new Date();
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth() + 1); // 1-12
  const [calTab, setCalTab] = useState('solar'); // solar | lunar
  const [notes, setNotes] = useState(loadNotes);
  const [modalDay, setModalDay] = useState(null); // { y, m, d, label }
  const [showNotifPanel, setShowNotifPanel] = useState(false);

  // Check due reminders on mount
  useEffect(() => {
    requestNotifPermission();
    checkDueReminders(notes);
  }, []);

  const saveAndUpdate = (updated) => {
    saveNotes(updated);
    setNotes(updated);
  };

  const prevMonth = () => {
    if (viewMonth === 1) { setViewMonth(12); setViewYear((y) => y - 1); }
    else setViewMonth((m) => m - 1);
  };
  const nextMonth = () => {
    if (viewMonth === 12) { setViewMonth(1); setViewYear((y) => y + 1); }
    else setViewMonth((m) => m + 1);
  };

  const daysInMonth = getDaysInMonth(viewYear, viewMonth);
  const firstDow = getFirstDayOfMonth(viewYear, viewMonth); // 0=Sun

  // Notification count
  const notifCount = Object.values(notes).reduce((acc, v) => acc + (v.reminders?.filter(r => !r.done).length || 0), 0);

  // Build calendar cells
  const cells = [];
  for (let i = 0; i < firstDow; i++) cells.push(null); // empty
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  const isToday = (d) =>
    d === today.getDate() && viewMonth === today.getMonth() + 1 && viewYear === today.getFullYear();

  const getDayNote = (d) => notes[dayKey(viewYear, viewMonth, d)];

  const openModal = (d) => {
    const lunar = getLunarFromSolar(viewYear, viewMonth, d);
    const lunarStr = lunar ? `Ngày ${lunar.getDay()} tháng ${lunar.getMonth()} ÂL` : '';
    setModalDay({
      y: viewYear, m: viewMonth, d,
      label: `${d}/${viewMonth}/${viewYear} ${lunarStr}`,
    });
  };

  // Year dropdown options
  const yearOpts = [];
  for (let y = viewYear - 5; y <= viewYear + 5; y++) yearOpts.push(y);

  return (
    <div className="space-y-4">
      {/* Calendar Header */}
      <div className="rounded-2xl overflow-hidden shadow-sm" style={{ border: '1px solid var(--color-surface-border)', background: 'var(--color-surface)' }}>
        {/* Controls row */}
        <div className="px-3 sm:px-4 py-3 flex flex-wrap items-center justify-between gap-2 border-b" style={{ borderColor: 'var(--color-surface-border)' }}>
          <div className="flex items-center gap-2">
            <button type="button" onClick={prevMonth}
              className="p-1.5 rounded-lg transition-colors hover:bg-black/5"
              style={{ color: 'var(--color-text-secondary)' }}>
              <IconChevronLeft size={18} />
            </button>

            <div className="flex items-center gap-1.5">
              <select
                value={viewMonth}
                onChange={(e) => setViewMonth(Number(e.target.value))}
                className="rounded-lg border-0 bg-transparent text-sm font-body font-semibold outline-none cursor-pointer"
                style={{ color: 'var(--color-primary)' }}>
                {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                  <option key={m} value={m}>Tháng {m}</option>
                ))}
              </select>
              <select
                value={viewYear}
                onChange={(e) => setViewYear(Number(e.target.value))}
                className="rounded-lg border-0 bg-transparent text-sm font-body font-semibold outline-none cursor-pointer"
                style={{ color: 'var(--color-primary)' }}>
                {yearOpts.map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>

            <button type="button" onClick={nextMonth}
              className="p-1.5 rounded-lg transition-colors hover:bg-black/5"
              style={{ color: 'var(--color-text-secondary)' }}>
              <IconChevronRight size={18} />
            </button>
          </div>

          <div className="flex items-center gap-2">
            {/* Solar / Lunar tab */}
            <div className="flex rounded-lg overflow-hidden border text-xs font-body" style={{ borderColor: 'var(--color-surface-border)' }}>
              <button type="button" onClick={() => setCalTab('solar')}
                className="px-3 py-1.5 transition-colors"
                style={{ background: calTab === 'solar' ? 'var(--color-primary)' : 'transparent', color: calTab === 'solar' ? 'var(--color-text-on-primary)' : 'var(--color-text-secondary)' }}>
                Dương Lịch
              </button>
              <button type="button" onClick={() => setCalTab('lunar')}
                className="px-3 py-1.5 transition-colors"
                style={{ background: calTab === 'lunar' ? 'var(--color-primary)' : 'transparent', color: calTab === 'lunar' ? 'var(--color-text-on-primary)' : 'var(--color-text-secondary)' }}>
                Âm Lịch
              </button>
            </div>

            {/* Notification bell */}
            <button type="button" onClick={() => setShowNotifPanel(true)}
              className="relative p-2 rounded-lg transition-colors hover:bg-black/5"
              style={{ color: 'var(--color-text-secondary)' }}>
              <IconBell size={18} />
              {notifCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center"
                  style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
                  {notifCount > 9 ? '9+' : notifCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Weekday headers */}
        <div className="grid grid-cols-7 border-b" style={{ borderColor: 'var(--color-surface-border)' }}>
          {WEEKDAYS.map((d, i) => (
            <div key={d} className="py-2 text-center text-[11px] font-body font-semibold"
              style={{ color: i === 0 ? '#c0392b' : i === 6 ? '#2980b9' : 'var(--color-text-secondary)' }}>
              {d}
            </div>
          ))}
        </div>

        {/* Days grid */}
        <div className="grid grid-cols-7">
          {cells.map((d, idx) => {
            if (!d) return <div key={`e-${idx}`} className="h-16 sm:h-20" />;
            const lunar = getLunarFromSolar(viewYear, viewMonth, d);
            const dayNote = getDayNote(d);
            const hasNote = dayNote && (dayNote.diary || dayNote.note || (dayNote.reminders?.length > 0));
            const isDone = dayNote?.diaryDone;
            const dow = (firstDow + d - 1) % 7;
            const isSun = dow === 0;
            const isSat = dow === 6;
            const _isToday = isToday(d);
            const lunarDay = lunar ? lunar.getDay() : null;
            const lunarMonth = lunar ? lunar.getMonth() : null;
            const isLunarFirst = lunarDay === 1;

            return (
              <div
                key={d}
                className="h-16 sm:h-20 p-1 relative group border-t border-r cursor-pointer transition-all hover:bg-black/[0.03]"
                style={{
                  borderColor: 'var(--color-surface-border)',
                  background: _isToday ? 'rgba(107,43,31,0.06)' : 'transparent',
                }}
                onClick={() => openModal(d)}
              >
                {/* Day number */}
                <div className="flex items-start justify-between">
                  <span
                    className="w-7 h-7 flex items-center justify-center rounded-full text-sm font-body font-semibold transition-colors"
                    style={{
                      background: _isToday ? 'var(--color-primary)' : 'transparent',
                      color: _isToday ? 'var(--color-text-on-primary)' : isSun ? '#c0392b' : isSat ? '#2980b9' : 'var(--color-text-primary)',
                    }}
                  >
                    {d}
                  </span>
                  {/* + button (hover) */}
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); openModal(d); }}
                    className="w-5 h-5 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ color: 'var(--color-primary)' }}
                  >
                    <IconPlus size={13} />
                  </button>
                </div>

                {/* Lunar day */}
                {calTab === 'lunar' || lunarDay ? (
                  <span className="text-[10px] font-body block leading-tight ml-0.5"
                    style={{ color: isLunarFirst ? 'var(--color-accent)' : 'var(--color-text-secondary)' }}>
                    {isLunarFirst ? `1/${lunarMonth}` : lunarDay}
                  </span>
                ) : null}

                {/* Indicators */}
                <div className="absolute bottom-1 left-1 flex gap-0.5">
                  {hasNote && !isDone && (
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--color-accent)' }} />
                  )}
                  {isDone && (
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--color-primary)' }} />
                  )}
                  {dayNote?.reminders?.filter(r => !r.done).length > 0 && (
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#2980b9' }} />
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="px-4 py-2 border-t flex flex-wrap items-center gap-3 text-[11px] font-body" style={{ borderColor: 'var(--color-surface-border)', color: 'var(--color-text-secondary)' }}>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: 'var(--color-accent)' }} />Có ghi chú</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: 'var(--color-primary)' }} />Đã hoàn thành</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: '#2980b9' }} />Có lịch nhắc</span>
        </div>
      </div>

      {/* Note Modal */}
      {modalDay && (
        <NoteModal
          dateKey={dayKey(modalDay.y, modalDay.m, modalDay.d)}
          dateLabel={modalDay.label}
          notes={notes}
          onSave={saveAndUpdate}
          onClose={() => setModalDay(null)}
        />
      )}

      {/* Notification Panel */}
      {showNotifPanel && (
        <NotificationPanel notes={notes} onClose={() => setShowNotifPanel(false)} />
      )}
    </div>
  );
}
