import React, { useState, useEffect, useCallback } from 'react';
import {
  IconPlus, IconX, IconMessageCircle, IconEye, IconArrowLeft,
  IconTrash, IconSend, IconUser, IconFilter, IconChevronRight,
  IconRefresh,
} from '@tabler/icons-react';
import { forumService } from '../../services/api';
import { useAuthStore } from '../../store/authStore';

// ============================================================
// Topic config
// ============================================================
const TOPICS = [
  { id: 'all', label: 'Tất cả', emoji: '🌐' },
  { id: 'chung', label: 'Hỏi Đáp Chung', emoji: '💬' },
  { id: 'tu-vi', label: 'Tử Vi Đẩu Số', emoji: '🔭' },
  { id: 'bat-tu', label: 'Bát Tự Tứ Trụ', emoji: '📊' },
  { id: 'kinh-dich', label: 'Kinh Dịch', emoji: '☯️' },
  { id: 'nhan-tuong', label: 'Nhân Tướng Học', emoji: '👁️' },
];

function topicLabel(id) {
  return TOPICS.find((t) => t.id === id) || TOPICS[0];
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const diff = Math.floor((Date.now() - d) / 1000);
  if (diff < 60) return 'Vừa xong';
  if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)} ngày trước`;
  return d.toLocaleDateString('vi-VN');
}

// ============================================================
// Create Post Modal
// ============================================================
function CreatePostModal({ onClose, onCreated }) {
  const [tieu_de, setTieuDe] = useState('');
  const [noi_dung, setNoiDung] = useState('');
  const [chu_de, setChuDe] = useState('chung');
  const [an_danh, setAnDanh] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await forumService.createPost({ tieu_de, noi_dung, chu_de, an_danh });
      onCreated(res.data?.du_lieu);
      onClose();
    } catch (err) {
      setError(err.response?.data?.loi || 'Đăng bài thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden"
        style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}>
        {/* Header */}
        <div className="px-5 pt-5 pb-3 border-b flex items-center justify-between" style={{ borderColor: 'var(--color-surface-border)' }}>
          <h3 className="font-body font-bold text-base" style={{ color: 'var(--color-primary)' }}>
            ✍️ Đăng bài mới
          </h3>
          <button type="button" onClick={onClose} style={{ color: 'var(--color-text-secondary)' }}><IconX size={18} /></button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-3">
          {error && (
            <p className="text-xs font-body p-2.5 rounded-lg" style={{ background: 'rgba(192,57,43,0.08)', color: '#c0392b' }}>
              {error}
            </p>
          )}

          {/* Chủ đề */}
          <div className="flex flex-wrap gap-1.5">
            {TOPICS.slice(1).map((t) => (
              <button key={t.id} type="button" onClick={() => setChuDe(t.id)}
                className="px-3 py-1.5 rounded-full text-xs font-body font-medium transition-all"
                style={{
                  background: chu_de === t.id ? 'var(--color-primary)' : 'var(--color-background)',
                  color: chu_de === t.id ? 'var(--color-text-on-primary)' : 'var(--color-text-secondary)',
                  border: '1px solid var(--color-surface-border)',
                }}>
                {t.emoji} {t.label}
              </button>
            ))}
          </div>

          <input
            type="text" value={tieu_de} onChange={(e) => setTieuDe(e.target.value)}
            placeholder="Tiêu đề bài viết..."
            className="w-full rounded-xl border px-3.5 py-2.5 text-sm font-body outline-none transition-colors"
            style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-primary)', background: 'var(--color-background)' }}
            required minLength={5}
          />
          <textarea
            rows={5} value={noi_dung} onChange={(e) => setNoiDung(e.target.value)}
            placeholder="Nội dung bài viết, câu hỏi, hoặc chia sẻ kinh nghiệm..."
            className="w-full resize-none rounded-xl border px-3.5 py-2.5 text-sm font-body outline-none"
            style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-primary)', background: 'var(--color-background)' }}
            required minLength={10}
          />

          {/* Anonymous toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <div
              className="w-10 h-5 rounded-full relative transition-colors flex-shrink-0"
              style={{ background: an_danh ? 'var(--color-primary)' : 'var(--color-surface-border)' }}
              onClick={() => setAnDanh((v) => !v)}
            >
              <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${an_danh ? 'translate-x-5' : 'translate-x-0.5'}`} />
            </div>
            <span className="text-xs font-body" style={{ color: 'var(--color-text-secondary)' }}>
              Đăng ẩn danh (tên hiển thị: "Ẩn Danh")
            </span>
          </label>

          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 py-2.5 rounded-xl text-sm font-body font-medium"
              style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-secondary)' }}>
              Hủy
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 py-2.5 rounded-xl text-sm font-body font-medium transition-opacity"
              style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)', opacity: loading ? 0.6 : 1 }}>
              {loading ? 'Đang đăng...' : 'Đăng bài'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================================
// Post Detail View (inline)
// ============================================================
function PostDetail({ postId, onBack }) {
  const user = useAuthStore((s) => s.user);
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [anDanhComment, setAnDanhComment] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const fetchPost = useCallback(async () => {
    setLoading(true);
    try {
      const res = await forumService.getPost(postId);
      setPost(res.data?.du_lieu);
    } catch { }
    setLoading(false);
  }, [postId]);

  useEffect(() => { fetchPost(); }, [fetchPost]);

  const handleComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim() || submitting) return;
    setSubmitting(true);
    try {
      const res = await forumService.createComment(postId, { noi_dung: commentText.trim(), an_danh: anDanhComment });
      if (res.data?.thanh_cong) {
        setCommentText('');
        fetchPost();
      }
    } catch { }
    setSubmitting(false);
  };

  const handleDeleteComment = async (cid) => {
    if (!window.confirm('Xóa bình luận này?')) return;
    try { await forumService.deleteComment(cid); fetchPost(); } catch { }
  };

  if (loading) return (
    <div className="text-center py-16 font-body text-sm" style={{ color: 'var(--color-text-secondary)' }}>
      Đang tải...
    </div>
  );
  if (!post) return (
    <div className="text-center py-16 font-body text-sm" style={{ color: 'var(--color-text-secondary)' }}>
      Không tìm thấy bài viết.
    </div>
  );

  const topic = topicLabel(post.chu_de);

  return (
    <div className="space-y-4">
      {/* Back */}
      <button type="button" onClick={onBack}
        className="flex items-center gap-1.5 text-sm font-body transition-colors"
        style={{ color: 'var(--color-text-secondary)' }}>
        <IconArrowLeft size={16} /> Quay lại diễn đàn
      </button>

      {/* Post card */}
      <div className="rounded-2xl p-5 space-y-3" style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}>
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-full text-xs font-body font-semibold"
            style={{ background: 'rgba(107,43,31,0.1)', color: 'var(--color-primary)' }}>
            {topic.emoji} {topic.label}
          </span>
          {post.an_danh && (
            <span className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>Ẩn danh</span>
          )}
        </div>
        <h2 className="font-body font-bold text-xl leading-snug" style={{ color: 'var(--color-text-primary)' }}>
          {post.tieu_de}
        </h2>
        <div className="flex items-center gap-3 text-xs font-body" style={{ color: 'var(--color-text-secondary)' }}>
          <span className="flex items-center gap-1"><IconUser size={12} />{post.ten_tac_gia}</span>
          <span className="flex items-center gap-1"><IconEye size={12} />{post.luot_xem} lượt xem</span>
          <span>{timeAgo(post.created_at)}</span>
        </div>
        <p className="font-body text-sm leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--color-text-primary)' }}>
          {post.noi_dung}
        </p>
        {post.la_cua_toi && (
          <button type="button"
            onClick={async () => { if (window.confirm('Xóa bài này?')) { await forumService.deletePost(post.id); onBack(); } }}
            className="flex items-center gap-1 text-xs font-body px-3 py-1.5 rounded-lg"
            style={{ color: '#c0392b', background: 'rgba(192,57,43,0.08)' }}>
            <IconTrash size={12} /> Xóa bài
          </button>
        )}
      </div>

      {/* Comments */}
      <div className="space-y-2">
        <h3 className="font-body font-semibold text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          Bình luận ({post.binh_luan?.length || 0})
        </h3>
        {post.binh_luan?.map((c) => (
          <div key={c.id} className="p-3.5 rounded-xl flex gap-3"
            style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}>
            <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center"
              style={{ background: 'rgba(107,43,31,0.12)' }}>
              <IconUser size={14} style={{ color: 'var(--color-primary)' }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-xs font-body font-semibold" style={{ color: 'var(--color-text-primary)' }}>{c.ten_tac_gia}</span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>{timeAgo(c.created_at)}</span>
                  {c.la_cua_toi && (
                    <button type="button" onClick={() => handleDeleteComment(c.id)}
                      className="p-1 rounded" style={{ color: '#c0392b' }}>
                      <IconTrash size={12} />
                    </button>
                  )}
                </div>
              </div>
              <p className="text-sm font-body mt-1 leading-relaxed" style={{ color: 'var(--color-text-primary)' }}>
                {c.noi_dung}
              </p>
            </div>
          </div>
        ))}
        {!post.binh_luan?.length && (
          <p className="text-sm text-center py-6 font-body" style={{ color: 'var(--color-text-secondary)' }}>
            Chưa có bình luận nào. Hãy là người đầu tiên!
          </p>
        )}
      </div>

      {/* Comment form */}
      <form onSubmit={handleComment} className="space-y-2">
        <textarea
          rows={3} value={commentText} onChange={(e) => setCommentText(e.target.value)}
          placeholder="Viết bình luận của bạn..."
          className="w-full resize-none rounded-xl border px-3.5 py-2.5 text-sm font-body outline-none"
          style={{ border: '1px solid var(--color-surface-border)', color: 'var(--color-text-primary)', background: 'var(--color-surface)' }}
        />
        <div className="flex items-center justify-between gap-3">
          <label className="flex items-center gap-1.5 cursor-pointer">
            <div className="w-8 h-4 rounded-full relative transition-colors flex-shrink-0"
              style={{ background: anDanhComment ? 'var(--color-primary)' : 'var(--color-surface-border)' }}
              onClick={() => setAnDanhComment((v) => !v)}>
              <span className={`absolute top-0.5 w-3 h-3 rounded-full bg-white shadow transition-transform ${anDanhComment ? 'translate-x-4' : 'translate-x-0.5'}`} />
            </div>
            <span className="text-xs font-body" style={{ color: 'var(--color-text-secondary)' }}>Ẩn danh</span>
          </label>
          <button type="submit" disabled={!commentText.trim() || submitting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-body font-medium transition-opacity"
            style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)', opacity: (!commentText.trim() || submitting) ? 0.5 : 1 }}>
            <IconSend size={14} /> Gửi
          </button>
        </div>
      </form>
    </div>
  );
}

// ============================================================
// Main ForumView
// ============================================================
export default function ForumView() {
  const [selectedTopic, setSelectedTopic] = useState('all');
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedPostId, setSelectedPostId] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const PAGE_SIZE = 20;

  const fetchPosts = useCallback(async (topicFilter, pg) => {
    setLoading(true);
    try {
      const params = { page: pg, page_size: PAGE_SIZE };
      if (topicFilter !== 'all') params.chu_de = topicFilter;
      const res = await forumService.getPosts(params);
      const data = res.data?.du_lieu;
      setPosts(data?.danh_sach || []);
      setTotal(data?.tong_so || 0);
    } catch { }
    setLoading(false);
  }, []);

  useEffect(() => {
    setPage(1);
    fetchPosts(selectedTopic, 1);
  }, [selectedTopic, fetchPosts]);

  if (selectedPostId) {
    return <PostDetail postId={selectedPostId} onBack={() => { setSelectedPostId(null); fetchPosts(selectedTopic, page); }} />;
  }

  return (
    <div className="space-y-4">
      {/* Topic filter tabs */}
      <div className="flex flex-wrap gap-2 items-center justify-between">
        <div className="flex flex-wrap gap-1.5">
          {TOPICS.map((t) => (
            <button key={t.id} type="button" onClick={() => setSelectedTopic(t.id)}
              className="px-3 py-1.5 rounded-full text-xs font-body font-medium transition-all"
              style={{
                background: selectedTopic === t.id ? 'var(--color-primary)' : 'var(--color-surface)',
                color: selectedTopic === t.id ? 'var(--color-text-on-primary)' : 'var(--color-text-secondary)',
                border: '1px solid var(--color-surface-border)',
              }}>
              {t.emoji} {t.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => fetchPosts(selectedTopic, page)}
            className="p-2 rounded-lg transition-colors"
            style={{ color: 'var(--color-text-secondary)' }}>
            <IconRefresh size={16} />
          </button>
          <button type="button" onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-body font-medium shadow-sm"
            style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
            <IconPlus size={16} /> Đăng bài
          </button>
        </div>
      </div>

      {/* Posts list */}
      {loading && posts.length === 0 && (
        <div className="text-center py-12 font-body text-sm" style={{ color: 'var(--color-text-secondary)' }}>Đang tải...</div>
      )}
      {!loading && posts.length === 0 && (
        <div className="text-center py-16 space-y-3">
          <p className="text-4xl">💬</p>
          <p className="font-body font-semibold" style={{ color: 'var(--color-text-primary)' }}>Chưa có bài viết nào</p>
          <p className="text-sm font-body" style={{ color: 'var(--color-text-secondary)' }}>Hãy là người đầu tiên chia sẻ!</p>
          <button type="button" onClick={() => setShowCreate(true)}
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-body font-medium"
            style={{ background: 'var(--color-primary)', color: 'var(--color-text-on-primary)' }}>
            <IconPlus size={16} /> Đăng bài đầu tiên
          </button>
        </div>
      )}
      <div className="space-y-2">
        {posts.map((p) => {
          const topic = topicLabel(p.chu_de);
          return (
            <div
              key={p.id}
              className="p-4 rounded-2xl cursor-pointer transition-all hover:shadow-md group"
              style={{ background: 'var(--color-surface)', border: '1px solid var(--color-surface-border)' }}
              onClick={() => setSelectedPostId(p.id)}
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5"
                  style={{ background: 'rgba(107,43,31,0.12)' }}>
                  <IconUser size={16} style={{ color: 'var(--color-primary)' }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[11px] font-body px-2 py-0.5 rounded-full"
                      style={{ background: 'rgba(107,43,31,0.08)', color: 'var(--color-primary)' }}>
                      {topic.emoji} {topic.label}
                    </span>
                    <span className="text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>
                      {p.ten_tac_gia} • {timeAgo(p.created_at)}
                    </span>
                  </div>
                  <h4 className="font-body font-semibold text-sm leading-snug group-hover:text-primary transition-colors line-clamp-1"
                    style={{ color: 'var(--color-text-primary)' }}>
                    {p.tieu_de}
                  </h4>
                  <p className="text-xs font-body mt-1 line-clamp-2 leading-relaxed"
                    style={{ color: 'var(--color-text-secondary)' }}>
                    {p.noi_dung_rut_gon}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0 text-[11px] font-body" style={{ color: 'var(--color-text-secondary)' }}>
                  <span className="flex items-center gap-1"><IconMessageCircle size={12} />{p.so_binh_luan}</span>
                  <span className="flex items-center gap-1"><IconEye size={12} />{p.luot_xem}</span>
                  <IconChevronRight size={14} className="mt-1 opacity-40 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create modal */}
      {showCreate && (
        <CreatePostModal
          onClose={() => setShowCreate(false)}
          onCreated={() => fetchPosts(selectedTopic, 1)}
        />
      )}
    </div>
  );
}
