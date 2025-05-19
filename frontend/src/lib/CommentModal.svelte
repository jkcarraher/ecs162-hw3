<script lang="ts">
  import { onMount } from 'svelte';
  export let selectedArticleId: string;
  export let onClose: () => void;
  export let articleHeadline: string;

  // We'll use an array of comment texts. Adjust as needed if you want a full comment object.
  let comments: string[] = [];
  let newComment: string = '';
  // Optional: For reply functionality (set this when replying to a comment)
  let parentCommentId: string | null = null;

  // Fetch only comments related to the selected article 
  async function fetchComments(): Promise<void> {
    try {
      const res = await fetch(`http://localhost:8000/api/comments/${selectedArticleId}`, {
        method: 'GET',
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        // Assuming data returns an array of comment documents; here we take only the commentText.
        comments = data.map((comment: any) => comment.commentText);
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
    if (newComment.trim() !== '') {
      const payload = {
        articleId: selectedArticleId,
        commentText: newComment,
        parentCommentId: parentCommentId // remains null for a top-level comment
      };

      try {
        const res = await fetch('http://localhost:8000/api/comment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include', // include cookies/sessions
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          comments = [...comments, data.commentText];
        } else {
          console.error('Error posting comment:', await res.text());
        }
      } catch (err) {
        console.error('Error posting comment:', err);
      }
      newComment = '';
    }
  }

  function handleOverlayClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }
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
    <div class="existing-comments">
      {#each comments as comment}
        <p class="comment">{comment}</p>
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
    margin-bottom: 15px;
  }

  .comments-header h3 {
    margin: 0;
    font-size: 1.1em;
  }

  .post-comment-section {
    display: flex;
    margin-bottom: 20px;
  }

  .post-comment-section textarea {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px 0 0 5px;
    resize: none;
  }

  .post-comment-section button {
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

  .comment {
    padding: 10px;
    border-bottom: 1px solid #eee;
  }

  .comment:last-child {
    border-bottom: none;
  }

  .no-comments {
    font-style: italic;
    color: #777;
  }
</style>