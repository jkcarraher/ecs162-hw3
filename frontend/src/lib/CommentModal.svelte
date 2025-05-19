<script lang="ts">
  import { onMount } from 'svelte';
  export let selectedArticleId: string;
  export let onClose: () => void;
  export let articleHeadline: string;
  export let userEmail: string;
  export let isModerator: boolean;

  let comments: any[] = [];
  let newComment: string = '';
  let newReply: string = '';
  let replyParentId: string | null = null;

  async function fetchComments(): Promise<void> {
    try {
      const res = await fetch(`http://localhost:8000/api/comments/${selectedArticleId}`, {
        method: 'GET',
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        comments = data;
      } else {
        console.error('Failed to load comments:', await res.text());
      }
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  }

  onMount(async () => {
    await fetchComments();
  });

  async function postComment(): Promise<void> {
    if (!userEmail) {
      alert("You must be logged in to post a comment.");
      return;
    }
    if (newComment.trim() !== '') {
      const payload = {
        articleId: selectedArticleId,
        commentText: newComment,
        parentCommentId: null
      };

      try {
        const res = await fetch('http://localhost:8000/api/comment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          comments = [...comments, data];
        } else {
          console.error('Error posting comment:', await res.text());
        }
      } catch (err) {
        console.error('Error posting comment:', err);
      }
      newComment = '';
    }
  }

  async function replyComment(): Promise<void> {
    if (!userEmail) {
      alert("You must be logged in to post a reply.");
      return;
    }
    if (newReply.trim() !== '' && replyParentId) {
      const payload = {
        articleId: selectedArticleId,
        commentText: newReply,
        parentCommentId: replyParentId
      };

      try {
        const res = await fetch('http://localhost:8000/api/comment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          comments = [...comments, data];
        } else {
          console.error('Error posting reply:', await res.text());
        }
      } catch (err) {
        console.error('Error posting reply:', err);
      }
      newReply = '';
      replyParentId = null;
    }
  }

  async function deleteComment(commentId: string): Promise<void> {
    try {
      const res = await fetch(`http://localhost:8000/api/comment/${commentId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (res.ok) {
        comments = comments.filter((comment) => comment._id !== commentId);
      } else {
        console.error('Error deleting comment:', await res.text());
      }
    } catch (err) {
      console.error('Error deleting comment:', err);
    }
  }

  function enableReply(commentId: string): void {
    replyParentId = commentId;
  }

  function handleOverlayClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }

  // Reactive block to sort comments: top-level comments in post order, with replies inserted after their parent
  $: sortedComments = (() => {
    const topLevel = comments.filter(c => !c.parentCommentId);
    const replies = comments.filter(c => c.parentCommentId);
    topLevel.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
    replies.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
    let combined = [];
    for (const parent of topLevel) {
      combined.push(parent);
      const children = replies.filter(reply => reply.parentCommentId === parent._id);
      combined.push(...children);
    }
    return combined;
  })();
</script>

<div class="comment-modal" on:click={handleOverlayClick}>
  <div class="modal-content">
    <div>
      <h2 class="article-title">{articleHeadline}</h2>
      <hr class="divider">
    </div>
    <div class="comments-header">
      <h3>Comments ({comments.length})</h3>
    </div>
    <div class="post-comment-section">
      <textarea placeholder="Leave a comment..." bind:value={newComment}></textarea>
      <button on:click={postComment}>Post</button>
    </div>

    {#if replyParentId}
      <div class="reply-section">
        <textarea placeholder="Write your reply..." bind:value={newReply}></textarea>
        <button on:click={replyComment}>Post Reply</button>
      </div>
    {/if}
    
    <div class="existing-comments">
      {#each sortedComments as comment}
        <div class="comment-item" class:reply={comment.parentCommentId}>
          <p class="comment">
            {#if comment.user?.name}
              {comment.user.name} - 
            {/if}
            {comment.commentText}
          </p>
          <div class="comment-actions">
            {#if !comment.parentCommentId && userEmail}
              <!-- Only allow replies to top-level comments when logged in -->
              <button class="reply-button" on:click={() => enableReply(comment._id)}>
                Reply
              </button>
            {/if}
            {#if comment.user?.email === userEmail || isModerator}
              <button class="delete-button" on:click={() => deleteComment(comment._id)}>
                Delete
              </button>
            {/if}
          </div>
        </div>
      {/each}
      {#if comments.length === 0}
        <p class="no-comments">No comments yet. Be the first to share your thoughts!</p>
      {/if}
    </div>
  </div>
</div>

<style>
  .comment-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    display: flex;
    justify-content: flex-end;
    align-items: stretch;
  }

  .modal-content {
    background-color: white;
    padding: 20px;
    width: 40%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .article-title {
    margin-bottom: 10px;
    font-size: 1.2em;
    font-weight: bold;
  }

  .divider {
    border: 0;
    height: 1px;
    background-color: #ccc;
    margin-bottom: 15px;
  }

  .comments-header {
    margin-bottom: 15px.
  }

  .comments-header h3 {
    margin: 0;
    font-size: 1.1em;
  }

  .post-comment-section,
  .reply-section {
    display: flex;
    margin-bottom: 20px;
  }

  .post-comment-section textarea,
  .reply-section textarea {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px 0 0 5px;
    resize: none;
  }

  .post-comment-section button,
  .reply-section button {
    padding: 10px 15px;
    background-color: #567B94;
    color: white;
    border: none;
    border-radius: 0 5px 5px 0;
    cursor: pointer;
  }

  .existing-comments {
    margin-bottom: 20px;
  }

  .comment-item {
    display: flex;
    flex-direction: column;
    padding: 10px;
    border-bottom: 1px solid #eee;
  }
  
  .reply {
    margin-left: 20px;
  }

  .comment {
    margin: 0 0 5px 0;
  }

  .comment-actions {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .delete-button {
    background: none;
    border: none;
    color: #727272;
    cursor: pointer;
    font-size: 0.9em;
  }
  
  .reply-button {
    background: none;
    border: none;
    color: #567B94;
    cursor: pointer;
    font-size: 0.9em;
  }

  .no-comments {
    font-style: italic;
    color: #777;
  }
</style>