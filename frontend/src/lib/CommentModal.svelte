<script lang="ts">
  export let selectedArticleId: string;
  export let comments: string[];
  export let onClose: () => void;
  export let articleHeadline: string;

  let newComment: string = '';

  async function postComment(): Promise<void> {
    if (newComment.trim() !== '') {
      console.log('Posting comment:', newComment, 'for article:', selectedArticleId);
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

  .close-button {
    margin-top: 20px;
    padding: 10px 15px;
    cursor: pointer;
    align-self: flex-start; /* Align to the left within the content area */
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
    resize: none; /* Prevent resizing */
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