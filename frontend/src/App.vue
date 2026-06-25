<template>
  <div id="app-container">
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <img src="/logo.jpg" alt="logo" class="header-logo" />
          <h2>工业数据采集网关</h2>
        </div>
        <div class="header-right">
          <el-tag :type="collectStatus.running ? 'success' : 'info'" size="large">
            {{ collectStatus.running ? '采集中' : '已停止' }}
          </el-tag>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px" class="app-aside">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/">
              <el-icon><Monitor /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/devices">
              <el-icon><Setting /></el-icon>
              <span>设备配置</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Tools /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
          </el-menu>
          <div class="author-info">
            <a href="https://www.zjzwfw.cloud/" target="_blank" rel="noopener">作者：谭策 | IT Online</a>
          </div>
        </el-aside>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const activeMenu = computed(() => route.path)

const collectStatus = ref({ running: false, devices: [], mqtt_connected: false })

let statusTimer = null

async function refreshStatus() {
  try {
    const res = await axios.get('/api/collect/status')
    if (res.data.success) {
      collectStatus.value = res.data.data
    }
  } catch (e) {
    // 忽略
  }
}

onMounted(() => {
  refreshStatus()
  statusTimer = setInterval(refreshStatus, 3000)
})

onUnmounted(() => {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app-container {
  height: 100vh;
  font-family: 'Microsoft YaHei', sans-serif;
}

.app-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-logo {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  object-fit: cover;
}

.app-header h2 {
  font-size: 18px;
  font-weight: 500;
}

.app-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.app-aside .el-menu {
  flex: 1;
  border-right: none;
}

.author-info {
  padding: 12px 16px;
  text-align: center;
  font-size: 12px;
  border-top: 1px solid #e4e7ed;
}

.author-info a {
  color: #909399;
  text-decoration: none;
}

.author-info a:hover {
  color: #409eff;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
  min-height: calc(100vh - 60px);
}
</style>
