<template>
    <div class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <h3>添加评论</h3>
        <textarea v-model="comment" placeholder="请输入评论..."></textarea>
        <div>
          <label>
            <input type="radio" v-model="visibility" value="public"> 公有
          </label>
          <label>
            <input type="radio" v-model="visibility" value="private"> 私有
          </label>
        </div>
        <button @click="submitComment">提交</button>
      </div>
    </div>
  </template>

<script>

export default {
  data () {
    return {
      comment: '',
      visibility: 'public' // 默认是公有
    }
  },
  methods: {
    closeDialog () {
      this.$emit('close')
    },
    submitComment () {
      this.$emit('submit', this.comment, this.visibility)
    }
  }
}
</script>
  <style scoped>
  .dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .dialog-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 300px;
  }

  textarea {
    width: 100%;
    height: 100px;
    margin-bottom: 10px;
  }

  button {
    width: 100%;
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }

  button:hover {
    background-color: #0056b3;
  }
</style>
