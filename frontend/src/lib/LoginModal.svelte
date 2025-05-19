<script lang="ts">
  export let userEmail: string;
  export let onLogout: () => void;
  export let onClose: () => void;
  
  function handleOverlayClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }
</script>

<div class="login-modal" on:click={handleOverlayClick}>
  <div class="modal-content" on:click|stopPropagation>
    <h2>Account Info</h2>
    <p>Logged in as {userEmail}</p>
    <button on:click={onLogout}>Logout</button>
  </div>
</div>

<style>
  .login-modal {
    position: fixed;
    top: 0;
    right: 0;
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
</style>