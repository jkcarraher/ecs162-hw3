<script lang="ts">
  import { onMount } from 'svelte';
  import type { Article } from './lib/Article.svelte';
  import { fetchApiKey, fetchArticles } from './lib/Article.svelte';
  import NYTHead from './assets/NewYorkTimesHead.png';
  import CommentIcon from './assets/comment.png';
  import CommentModal from './lib/CommentModal.svelte';
  import LoginModal from './lib/LoginModal.svelte';

  let date: string = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  let apiKey: string = '';
  let articles: Article[] = [];
  let page: number = 0;
  let selectedArticleId: string | null = null;
  let showModal: boolean = false;
  let comments: string[] = [];
  let commentCounts: { [articleUrl: string]: number } = {};

  let loggedIn: boolean = false; 
  let showLoginModal: boolean = false;
  let userEmail: string = '';

  async function fetchComments(articleId: string): Promise<string[]> {
    return [`Comment 1 for article ${articleId}`, `Another thought on article ${articleId}`];
  }

  async function handleCommentButtonClick(articleId: string): Promise<void> {
    selectedArticleId = articleId;
    comments = await fetchComments(articleId);
    showModal = true;
  }

  function closeModal(): void {
    showModal = false;
    selectedArticleId = null;
    comments = [];
  }

  function handleLoginButtonClick(): void {
    if (!loggedIn) {
      window.location.href = 'http://localhost:8000/login';
    } else {
      showLoginModal = true;
    }
  }

  function closeLoginModal(): void {
    showLoginModal = false;
  }

  function logout(): void {
    window.location.href = 'http://localhost:8000/logout';
  }

  async function updateOnScroll(): Promise<void> {
    const bottomOfPage = window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
    if (bottomOfPage) {
      page += 1;
      let newArticles = await fetchArticles(apiKey, page);
      articles = [...articles, ...newArticles];
    }
  }

  async function checkLogin(): Promise<void> {
    try {
      const res = await fetch('/api/user');
      if (res.ok) {
        const data = await res.json();
        userEmail = data.email || '';
        loggedIn = true;
      } else {
        loggedIn = false;
        userEmail = '';
      }
    } catch (err) {
      console.error('Failed to check login status:', err);
      loggedIn = false;
      userEmail = '';
    }
  }

  onMount(async () => {
    apiKey = await fetchApiKey();
    if (apiKey) {
      try {
        let newArticles = await fetchArticles(apiKey, page);
        articles = [...articles, ...newArticles];
      } catch (e) {
        console.error('Failed to fetch articles:', (e as Error).message);
      }
    } else {
      console.error('API key was not fetched, cannot fetch articles.');
      articles = [];
    }
    // Call the /api/user route in the backend to set login state
    await checkLogin();
    
    window.addEventListener('scroll', updateOnScroll);
  });
</script>

<main>
  <header>
    {#if !loggedIn}
      <button class="login-button" on:click={handleLoginButtonClick}>LOG IN</button>
    {:else}
      <button class="account-button" on:click={handleLoginButtonClick}>
        Account <span class="caret">▼</span>
      </button>
    {/if}
    <img src={NYTHead} alt="New York Times logo" class="nyt-head">
    <div class="page-info">
      <p class="page-date">{date}</p>
      <span class="page-meta">Today's Paper</span>
    </div>
    <nav>
      <ul>
        <li>U.S.</li>
        <li>World</li>
        <li>Business</li>
        <li>Arts</li>
        <li>Lifestyle</li>
        <li>Opinion</li>
        <li>Audio</li>
        <li>Games</li>
        <li>Cooking</li>
      </ul>
    </nav>
  </header>
  <hr>
  <div class="column-container">
    {#each articles as article (article.url)}
      <article class="column">
        <img class="article-img" src={article.img_url} alt={article.img_cap}>
        <h2>
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.headline}
          </a>
        </h2>
        <p>{article.snippet}</p>
        <div class="article-info">
          <small>{article.published.toLocaleDateString()}</small>
          <div class="article-actions">
            <button class="comment-button" on:click={() => handleCommentButtonClick(article.url)}>
              <img src={CommentIcon} alt="Comment Icon" class="comment-icon">
              <span class="comment-count">{commentCounts[article.url] || 0}</span>
            </button>
          </div>
        </div>
      </article>
    {/each}
  </div>

  {#if showModal && selectedArticleId}
    <CommentModal
      {selectedArticleId}
      {comments}
      onClose={closeModal}
      articleHeadline={articles.find(article => article.url === selectedArticleId)?.headline || 'Article Title'}
    />
  {/if}
  
  {#if showLoginModal}
    <LoginModal 
      userEmail={userEmail} 
      onLogout={logout} 
      onClose={closeLoginModal} />
  {/if}
</main>