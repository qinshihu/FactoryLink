<template>
  <div class="home-page">
    <div class="page-header">
      <h3>设备列表</h3>
      <div class="header-actions">
        <el-button type="success" @click="startCollect" :disabled="collectStatus.running">
          <el-icon><VideoPlay /></el-icon> 启动采集
        </el-button>
        <el-button type="danger" @click="stopCollect" :disabled="!collectStatus.running">
          <el-icon><VideoPause /></el-icon> 停止采集
        </el-button>
      </div>
    </div>

    <!-- 设备卡片 -->
    <el-row :gutter="20" v-if="devices.length > 0">
      <el-col :span="8" v-for="device in devices" :key="device.id" style="margin-bottom: 20px">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ device.name }}</span>
              <el-tag :type="getDeviceStatus(device.id) === 'online' ? 'success' : 'danger'" size="small">
                {{ getDeviceStatus(device.id) === 'online' ? '在线' : '离线' }}
              </el-tag>
            </div>
          </template>
          <div class="device-info">
            <p><strong>协议：</strong>{{ getProtocolLabel(device.protocol) }}</p>
            <p><strong>地址：</strong>{{ device.ip || device.port || '-' }}</p>
            <p><strong>点位数量：</strong>{{ device.points?.length || 0 }}</p>
          </div>
          <div class="device-data" v-if="deviceData[device.id]">
            <el-divider />
            <p class="data-title">实时数据：</p>
            <div v-for="(val, key) in deviceData[device.id]" :key="key" class="data-item">
              <span class="data-name">{{ key }}：</span>
              <span class="data-value" :class="{ 'data-bad': val.quality === 'bad' }">
                {{ val.value !== null && val.value !== undefined ? val.value + ' ' + val.unit : '---' }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-else description="暂无设备，请先添加设备" />

    <!-- 连接状态 -->
    <div class="status-bar">
      <span>MQTT：</span>
      <el-tag :type="collectStatus.mqtt_connected ? 'success' : 'info'" size="small">
        {{ collectStatus.mqtt_connected ? '已连接' : '未连接' }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const devices = ref([])
const collectStatus = ref({ running: false, devices: [], mqtt_connected: false })
const deviceData = ref({})
let ws = null
let wsRetryCount = 0
const WS_MAX_RETRIES = 10

const protocolLabels = {
  modbus_tcp: 'Modbus TCP',
  modbus_rtu: 'Modbus RTU',
  s7: '西门子S7',
  mitsubishi: '三菱MC'
}

function getProtocolLabel(protocol) {
  return protocolLabels[protocol] || protocol
}

function getDeviceStatus(deviceId) {
  const ds = collectStatus.value.devices.find(d => d.device_id === deviceId)
  return ds?.connected ? 'online' : 'offline'
}

async function loadDevices() {
  try {
    const res = await axios.get('/api/devices')
    if (res.data.success) {
      devices.value = res.data.data
    }
  } catch (e) {
    console.error('加载设备列表失败', e)
  }
}

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

async function startCollect() {
  try {
    await axios.post('/api/collect/start')
    refreshStatus()
  } catch (e) {
    console.error('启动采集失败', e)
  }
}

async function stopCollect() {
  try {
    await axios.post('/api/collect/stop')
    refreshStatus()
  } catch (e) {
    console.error('停止采集失败', e)
  }
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/data`
  ws = new WebSocket(wsUrl)

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      if (msg.type === 'data') {
        deviceData.value[msg.device_id] = msg.values
      } else if (msg.type === 'status') {
        refreshStatus()
      }
    } catch (e) {
      // 忽略
    }
  }

  ws.onclose = () => {
    if (wsRetryCount < WS_MAX_RETRIES) {
      const delay = Math.min(1000 * Math.pow(2, wsRetryCount), 30000)
      wsRetryCount++
      setTimeout(connectWebSocket, delay)
    }
  }

  ws.onopen = () => {
    wsRetryCount = 0
  }
}

onMounted(() => {
  loadDevices()
  refreshStatus()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.home-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h3 {
  font-size: 16px;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-info p {
  margin: 5px 0;
  font-size: 13px;
  color: #606266;
}

.data-title {
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 13px;
}

.data-item {
  margin: 3px 0;
  font-size: 13px;
}

.data-name {
  color: #909399;
}

.data-value {
  color: #303133;
  font-weight: 500;
}

.data-bad {
  color: #f56c6c;
}

.status-bar {
  margin-top: 20px;
  padding: 10px;
  background: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
</style>
