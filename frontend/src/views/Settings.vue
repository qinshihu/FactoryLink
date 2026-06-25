<template>
  <div class="settings-page">
    <h3>系统设置</h3>

    <!-- MQTT配置 -->
    <el-card class="settings-card">
      <template #header>
        <span>MQTT配置</span>
      </template>
      <el-form :model="mqttForm" label-width="120px">
        <el-form-item label="启用MQTT">
          <el-switch v-model="mqttForm.enabled" />
        </el-form-item>
        <el-form-item label="服务器地址">
          <el-input v-model="mqttForm.host" placeholder="192.168.1.200" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="mqttForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="客户端ID">
          <el-input v-model="mqttForm.client_id" placeholder="gateway-001" />
        </el-form-item>
        <el-form-item label="Topic前缀">
          <el-input v-model="mqttForm.topic_prefix" placeholder="factory/data" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="mqttForm.username" placeholder="可选" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="mqttForm.password" type="password" placeholder="可选" show-password />
        </el-form-item>
        <el-form-item label="QoS">
          <el-select v-model="mqttForm.qos">
            <el-option :value="0" label="0 - 最多一次" />
            <el-option :value="1" label="1 - 至少一次" />
            <el-option :value="2" label="2 - 仅一次" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveMqtt">保存MQTT配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 采集设置 -->
    <el-card class="settings-card">
      <template #header>
        <span>采集设置</span>
      </template>
      <el-form :model="collectForm" label-width="120px">
        <el-form-item label="采集间隔(ms)">
          <el-input-number v-model="collectForm.collect_interval" :min="100" :max="60000" :step="100" />
          <span class="form-tip">当前: {{ (collectForm.collect_interval / 1000).toFixed(1) }}秒</span>
        </el-form-item>
        <el-form-item label="网关名称">
          <el-input v-model="collectForm.gateway_name" placeholder="车间1号网关" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveCollect">保存采集设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 重连策略 -->
    <el-card class="settings-card">
      <template #header>
        <span>重连策略</span>
      </template>
      <el-form :model="reconnectForm" label-width="140px">
        <el-form-item label="最大重试次数">
          <el-input-number v-model="reconnectForm.max_retries" :min="0" :max="100" />
          <span class="form-tip">0 = 无限重试</span>
        </el-form-item>
        <el-form-item label="基础延迟(秒)">
          <el-input-number v-model="reconnectForm.base_delay" :min="1" :max="60" />
        </el-form-item>
        <el-form-item label="最大延迟(秒)">
          <el-input-number v-model="reconnectForm.max_delay" :min="10" :max="300" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveReconnect">保存重连策略</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 开机自启动 -->
    <el-card class="settings-card">
      <template #header>
        <span>开机自启动</span>
      </template>
      <el-form label-width="120px">
        <el-form-item label="开机自启动">
          <el-switch v-model="autostartEnabled" @change="toggleAutostart" />
          <span class="form-tip" style="margin-left: 10px">
            {{ autostartEnabled ? '已启用' : '未启用' }}
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI配置助手 -->
    <el-card class="settings-card">
      <template #header>
        <span>AI配置助手</span>
      </template>
      <el-form :model="aiForm" label-width="120px">
        <el-form-item label="启用AI助手">
          <el-switch v-model="aiForm.enabled" />
          <span class="form-tip" style="margin-left: 10px">
            在设备配置页面显示AI对话面板
          </span>
        </el-form-item>
        <el-form-item label="API地址">
          <el-input v-model="aiForm.api_url" placeholder="https://api.openai.com/v1">
            <template #prepend>URL</template>
          </el-input>
          <div class="form-tip" style="margin-top: 4px">
            支持OpenAI兼容接口（通义千问、DeepSeek等），默认OpenAI格式
          </div>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="aiForm.api_key" type="password" show-password placeholder="sk-..." />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="aiForm.model" placeholder="gpt-3.5-turbo">
            <template #prepend>Model</template>
          </el-input>
          <div class="form-tip" style="margin-top: 4px">
            如 gpt-4o / qwen-turbo / deepseek-chat
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveAI">保存AI配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 应用配置 -->
    <el-card class="settings-card">
      <template #header>
        <span>应用配置</span>
      </template>
      <p style="color: #909399; margin-bottom: 10px; font-size: 13px">
        修改以上配置后，点击"应用配置"按钮将保存并重启采集器。
      </p>
      <el-button type="success" @click="applyConfig" size="large">
        <el-icon><Check /></el-icon> 应用配置（保存并重启采集）
      </el-button>
    </el-card>

    <!-- 日志查看 -->
    <el-card class="settings-card">
      <template #header>
        <div class="log-header">
          <span>日志查看</span>
          <div>
            <el-select v-model="logLevel" @change="loadLogs" size="small" style="width: 120px; margin-right: 10px">
              <el-option value="" label="全部级别" />
              <el-option value="INFO" label="INFO" />
              <el-option value="WARNING" label="WARNING" />
              <el-option value="ERROR" label="ERROR" />
              <el-option value="DEBUG" label="DEBUG" />
            </el-select>
            <el-button size="small" @click="loadLogs">刷新</el-button>
            <el-button size="small" type="danger" @click="clearLogs">清空显示</el-button>
          </div>
        </div>
      </template>
      <div class="log-container">
        <div v-if="logs.length === 0" style="text-align: center; color: #909399; padding: 20px">
          暂无日志
        </div>
        <div v-for="(log, index) in logs" :key="index" class="log-line" :class="getLogClass(log)">
          {{ log }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const mqttForm = ref({
  enabled: false,
  host: '',
  port: 1883,
  client_id: 'gateway-001',
  topic_prefix: 'factory/data',
  username: '',
  password: '',
  qos: 1
})

const collectForm = ref({
  gateway_name: '默认网关',
  collect_interval: 1000
})

const reconnectForm = ref({
  max_retries: 0,
  base_delay: 1,
  max_delay: 60
})

const autostartEnabled = ref(false)
const logs = ref([])
const logLevel = ref('')

const aiForm = ref({
  enabled: false,
  api_url: 'https://api.openai.com/v1',
  api_key: '',
  model: 'gpt-3.5-turbo'
})

async function loadConfig() {
  try {
    const res = await axios.get('/api/config')
    if (res.data.success) {
      const config = res.data.data
      if (config.mqtt) {
        mqttForm.value = { ...mqttForm.value, ...config.mqtt }
      }
      collectForm.value.gateway_name = config.gateway_name || '默认网关'
      collectForm.value.collect_interval = config.collect_interval || 1000
      if (config.reconnect) {
        reconnectForm.value = { ...reconnectForm.value, ...config.reconnect }
      }
    }
  } catch (e) {
    console.error('加载配置失败', e)
  }
}

async function loadAutostart() {
  try {
    const res = await axios.get('/api/system/autostart')
    if (res.data.success) {
      autostartEnabled.value = res.data.data.enabled
    }
  } catch (e) {
    // 忽略
  }
}

async function saveMqtt() {
  try {
    await axios.put('/api/mqtt', mqttForm.value)
    ElMessage.success('MQTT配置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function saveCollect() {
  try {
    const config = {
      gateway_name: collectForm.value.gateway_name,
      collect_interval: collectForm.value.collect_interval
    }
    await axios.put('/api/config', {
      ...(await axios.get('/api/config')).data.data,
      ...config
    })
    ElMessage.success('采集设置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function saveReconnect() {
  try {
    const res = await axios.get('/api/config')
    const config = res.data.data
    config.reconnect = reconnectForm.value
    await axios.put('/api/config', config)
    ElMessage.success('重连策略已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function applyConfig() {
  try {
    await axios.post('/api/config/apply')
    ElMessage.success('配置已应用，采集器正在重启')
  } catch (e) {
    ElMessage.error('应用失败')
  }
}

async function toggleAutostart(val) {
  try {
    await axios.post('/api/system/autostart', null, { params: { enabled: val } })
    ElMessage.success(val ? '已设置开机自启动' : '已取消开机自启动')
  } catch (e) {
    ElMessage.error('设置失败')
    autostartEnabled.value = !val
  }
}

async function loadAIConfig() {
  try {
    const res = await axios.get('/api/ai/config')
    if (res.data.success && res.data.data) {
      aiForm.value = { ...aiForm.value, ...res.data.data }
    }
  } catch (e) {
    // 忽略
  }
}

async function saveAI() {
  try {
    await axios.put('/api/ai/config', aiForm.value)
    ElMessage.success('AI配置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function loadLogs() {
  try {
    const params = { lines: 200 }
    if (logLevel.value) {
      params.level = logLevel.value
    }
    const res = await axios.get('/api/logs', { params })
    if (res.data.success) {
      logs.value = res.data.data
    }
  } catch (e) {
    console.error('加载日志失败', e)
  }
}

function clearLogs() {
  logs.value = []
}

function getLogClass(log) {
  if (log.includes('[ERROR]')) return 'log-error'
  if (log.includes('[WARNING]')) return 'log-warning'
  if (log.includes('[DEBUG]')) return 'log-debug'
  return 'log-info'
}

onMounted(() => {
  loadConfig()
  loadAutostart()
  loadAIConfig()
  loadLogs()
})
</script>

<style scoped>
.settings-page {
  max-width: 900px;
}

.settings-page h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  max-height: 400px;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.log-line {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-error {
  color: #f44747;
}

.log-warning {
  color: #cca700;
}

.log-debug {
  color: #808080;
}

.log-info {
  color: #d4d4d4;
}
</style>
