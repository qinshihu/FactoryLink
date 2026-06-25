<template>
  <div class="device-config-page">
    <div class="page-header">
      <h3>设备配置</h3>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon> 添加设备
        </el-button>
        <el-upload
          :auto-upload="false"
          :on-change="handleExcelImport"
          accept=".xlsx,.xls"
          :show-file-list="false"
          style="display: inline-block; margin-left: 10px"
        >
          <el-button type="success">
            <el-icon><Upload /></el-icon> 导入Excel
          </el-button>
        </el-upload>
        <el-button @click="downloadTemplate" style="margin-left: 10px">
          <el-icon><Download /></el-icon> 下载模板
        </el-button>
      </div>
    </div>

    <!-- AI助手面板 -->
    <el-collapse v-if="aiEnabled" v-model="aiPanelActive" class="ai-panel">
      <el-collapse-item title="AI 配置助手" name="ai">
        <template #title>
          <div class="ai-panel-title">
            <el-icon><MagicStick /></el-icon>
            <span>AI 配置助手</span>
            <el-tag size="small" type="warning" style="margin-left: 8px">Beta</el-tag>
          </div>
        </template>
        <div class="ai-chat-area">
          <!-- 示例提示 -->
          <div v-if="!aiStreaming && !aiPreview" class="ai-examples">
            <span class="ai-examples-label">试试这样说：</span>
            <div
              v-for="(example, idx) in aiExamples"
              :key="idx"
              class="ai-example-item"
              @click="aiInput = example"
            >
              <el-icon class="ai-example-icon"><ChatDotRound /></el-icon>
              <span>{{ example }}</span>
            </div>
          </div>

          <!-- 流式输出中 -->
          <div v-if="aiStreaming" class="ai-streaming-box">
            <div class="ai-streaming-header">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>AI正在生成配置...</span>
            </div>
            <pre class="ai-streaming-content">{{ aiStreamContent }}</pre>
          </div>

          <!-- 可编辑预览卡片 -->
          <div v-if="aiPreview" class="ai-preview-card">
            <div class="ai-preview-header">
              <el-icon style="color: #67c23a"><CircleCheck /></el-icon>
              <span>AI 已生成设备配置，请确认或修改后填入表单</span>
              <el-button size="small" text @click="aiPreview = null; aiStreamContent = ''">关闭</el-button>
            </div>
            <el-form :model="aiPreviewForm" label-width="80px" size="small" class="ai-preview-form">
              <el-row :gutter="12">
                <el-col :span="12">
                  <el-form-item label="设备名称">
                    <el-input v-model="aiPreviewForm.name" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="协议类型">
                    <el-select v-model="aiPreviewForm.protocol" style="width: 100%">
                      <el-option label="Modbus TCP" value="modbus_tcp" />
                      <el-option label="Modbus RTU" value="modbus_rtu" />
                      <el-option label="西门子S7" value="s7" />
                      <el-option label="三菱MC" value="mitsubishi" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="12" v-if="aiPreviewForm.protocol !== 'modbus_rtu'">
                <el-col :span="12">
                  <el-form-item label="IP地址">
                    <el-input v-model="aiPreviewForm.ip" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="端口">
                    <el-input-number v-model="aiPreviewForm.port" :min="1" :max="65535" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="12" v-if="aiPreviewForm.protocol === 'modbus_rtu'">
                <el-col :span="12">
                  <el-form-item label="串口号">
                    <el-input v-model="aiPreviewForm.com_port" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="波特率">
                    <el-select v-model="aiPreviewForm.baudrate" style="width: 100%">
                      <el-option :value="9600" label="9600" />
                      <el-option :value="19200" label="19200" />
                      <el-option :value="38400" label="38400" />
                      <el-option :value="115200" label="115200" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="12">
                <el-col :span="12" v-if="aiPreviewForm.protocol.startsWith('modbus')">
                  <el-form-item label="从站ID">
                    <el-input-number v-model="aiPreviewForm.slave_id" :min="1" :max="247" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12" v-if="aiPreviewForm.protocol === 's7'">
                  <el-form-item label="机架/插槽">
                    <el-input-number v-model="aiPreviewForm.rack" :min="0" :max="31" size="small" style="width: 70px" />
                    <span style="margin: 0 4px; color: #909399">/</span>
                    <el-input-number v-model="aiPreviewForm.slot" :min="0" :max="31" size="small" style="width: 70px" />
                  </el-form-item>
                </el-col>
                <el-col :span="12" v-if="aiPreviewForm.protocol === 'mitsubishi'">
                  <el-form-item label="PLC型号">
                    <el-select v-model="aiPreviewForm.plc_type" style="width: 100%">
                      <el-option value="FX5U" label="FX5U" />
                      <el-option value="Q系列" label="Q系列" />
                      <el-option value="L系列" label="L系列" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="点位列表">
                <div class="ai-preview-points">
                  <div v-for="(pt, idx) in aiPreviewForm.points" :key="idx" class="ai-preview-point-row">
                    <el-input v-model="pt.name" placeholder="名称" size="small" style="width: 90px" />
                    <el-input v-model="pt.address" placeholder="地址" size="small" style="width: 110px" />
                    <el-select v-model="pt.type" size="small" style="width: 80px">
                      <el-option value="bool" label="bool" />
                      <el-option value="int16" label="int16" />
                      <el-option value="uint16" label="uint16" />
                      <el-option value="int32" label="int32" />
                      <el-option value="float" label="float" />
                      <el-option value="double" label="double" />
                    </el-select>
                    <el-input v-model="pt.unit" placeholder="单位" size="small" style="width: 60px" />
                    <el-button size="small" type="danger" :icon="Delete" circle @click="aiPreviewForm.points.splice(idx, 1)" />
                  </div>
                  <el-button size="small" type="primary" plain @click="aiPreviewForm.points.push({ name: '', address: '', type: 'float', rate: 1, offset: 0, unit: '' })">
                    + 添加点位
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
            <div class="ai-preview-actions">
              <el-button @click="aiRetry" :loading="aiStreaming">
                <el-icon><Refresh /></el-icon> 重新生成
              </el-button>
              <el-button type="primary" @click="applyAIPreview">
                <el-icon><Check /></el-icon> 确认并填入表单
              </el-button>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="aiError" class="ai-result-error">
            <el-icon><CircleClose /></el-icon>
            <span>{{ aiError }}</span>
            <el-button size="small" text type="danger" @click="aiRetry" style="margin-left: 8px">重试</el-button>
          </div>

          <!-- 输入框 -->
          <div class="ai-input-area">
            <el-input
              v-model="aiInput"
              placeholder="描述你的设备，如：帮我添加一台192.168.1.100的西门子S7-1200，采集DB3里偏移0开始的10个浮点数，单位是℃"
              @keyup.enter="aiParse"
              :disabled="aiStreaming"
              clearable
            >
              <template #append>
                <el-button @click="aiParse" :loading="aiStreaming" :disabled="!aiInput.trim()">
                  发送
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 设备列表 -->
    <el-table :data="devices" border stripe style="width: 100%">
      <el-table-column prop="name" label="设备名称" min-width="150" />
      <el-table-column label="协议" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ getProtocolLabel(row.protocol) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip" label="IP/端口" width="180">
        <template #default="{ row }">
          {{ row.ip || row.port || '-' }}{{ row.port && row.protocol !== 'modbus_rtu' ? ':' + row.port : '' }}
        </template>
      </el-table-column>
      <el-table-column label="点位数量" width="100">
        <template #default="{ row }">
          {{ row.points?.length || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" @change="toggleDevice(row)" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editDevice(row)">编辑</el-button>
          <el-button size="small" type="success" @click="testDevice(row)">测试连接</el-button>
          <el-button size="small" type="danger" @click="deleteDevice(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑设备对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑设备' : '添加设备'"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="设备名称">
          <el-input v-model="form.name" placeholder="如：西门子S7-1200" />
        </el-form-item>
        <el-form-item label="协议类型">
          <el-select v-model="form.protocol" @change="onProtocolChange" style="width: 100%">
            <el-option label="Modbus TCP" value="modbus_tcp" />
            <el-option label="Modbus RTU" value="modbus_rtu" />
            <el-option label="西门子S7" value="s7" />
            <el-option label="三菱MC" value="mitsubishi" />
          </el-select>
        </el-form-item>

        <!-- Modbus TCP / S7 / 三菱MC 通用 -->
        <el-form-item label="IP地址" v-if="form.protocol !== 'modbus_rtu'">
          <el-input v-model="form.ip" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item label="端口" v-if="form.protocol !== 'modbus_rtu'">
          <el-input-number v-model="form.port" :min="1" :max="65535" />
        </el-form-item>

        <!-- Modbus RTU -->
        <template v-if="form.protocol === 'modbus_rtu'">
          <el-form-item label="串口号">
            <el-input v-model="form.com_port" placeholder="COM3" />
          </el-form-item>
          <el-form-item label="波特率">
            <el-select v-model="form.baudrate">
              <el-option :value="9600" label="9600" />
              <el-option :value="19200" label="19200" />
              <el-option :value="38400" label="38400" />
              <el-option :value="115200" label="115200" />
            </el-select>
          </el-form-item>
          <el-form-item label="校验位">
            <el-select v-model="form.parity">
              <el-option value="N" label="无校验(N)" />
              <el-option value="E" label="偶校验(E)" />
              <el-option value="O" label="奇校验(O)" />
            </el-select>
          </el-form-item>
          <el-form-item label="数据位">
            <el-input-number v-model="form.databits" :min="5" :max="8" />
          </el-form-item>
          <el-form-item label="停止位">
            <el-input-number v-model="form.stopbits" :min="1" :max="2" />
          </el-form-item>
        </template>

        <!-- Modbus 从站ID -->
        <el-form-item label="从站ID" v-if="form.protocol.startsWith('modbus')">
          <el-input-number v-model="form.slave_id" :min="1" :max="247" />
        </el-form-item>

        <!-- S7 -->
        <template v-if="form.protocol === 's7'">
          <el-form-item label="机架号">
            <el-input-number v-model="form.rack" :min="0" :max="31" />
          </el-form-item>
          <el-form-item label="插槽号">
            <el-input-number v-model="form.slot" :min="0" :max="31" />
          </el-form-item>
        </template>

        <!-- 三菱MC -->
        <el-form-item label="PLC型号" v-if="form.protocol === 'mitsubishi'">
          <el-select v-model="form.plc_type">
            <el-option value="FX5U" label="FX5U" />
            <el-option value="Q系列" label="Q系列" />
            <el-option value="L系列" label="L系列" />
          </el-select>
        </el-form-item>

        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>

        <!-- 点位配置 -->
        <el-divider>点位配置</el-divider>
        <div class="points-section">
          <el-button size="small" type="primary" @click="addPoint" style="margin-bottom: 10px">
            + 添加点位
          </el-button>
          <el-table :data="form.points" border size="small">
            <el-table-column label="点位名称" width="120">
              <template #default="{ row, $index }">
                <el-input v-model="row.name" size="small" placeholder="如：温度1" />
              </template>
            </el-table-column>
            <el-table-column label="地址" width="150">
              <template #default="{ row, $index }">
                <el-input v-model="row.address" size="small" placeholder="如：DB1.DBD0" />
              </template>
            </el-table-column>
            <el-table-column label="数据类型" width="100">
              <template #default="{ row, $index }">
                <el-select v-model="row.type" size="small">
                  <el-option value="bool" label="bool" />
                  <el-option value="int16" label="int16" />
                  <el-option value="uint16" label="uint16" />
                  <el-option value="int32" label="int32" />
                  <el-option value="uint32" label="uint32" />
                  <el-option value="float" label="float" />
                  <el-option value="double" label="double" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="倍率" width="70">
              <template #default="{ row }">
                <el-input-number v-model="row.rate" size="small" :min="0.001" :step="0.1" />
              </template>
            </el-table-column>
            <el-table-column label="偏移" width="70">
              <template #default="{ row }">
                <el-input-number v-model="row.offset" size="small" :step="0.1" />
              </template>
            </el-table-column>
            <el-table-column label="单位" width="80">
              <template #default="{ row }">
                <el-input v-model="row.unit" size="small" placeholder="℃" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button size="small" type="danger" @click="removePoint($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDevice">保存</el-button>
      </template>
    </el-dialog>

    <!-- 测试连接结果 -->
    <el-dialog v-model="testDialogVisible" title="测试连接" width="400px">
      <div v-if="testing" style="text-align: center; padding: 20px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p>正在测试连接...</p>
      </div>
      <el-result v-else :icon="testResult.success ? 'success' : 'error'" :title="testResult.success ? '连接成功' : '连接失败'">
        <template #sub-title>
          <p>{{ testResult.message }}</p>
        </template>
      </el-result>
    </el-dialog>

    <!-- Excel导入预览 -->
    <el-dialog v-model="excelPreviewVisible" title="Excel导入预览" width="700px" :close-on-click-modal="false">
      <div v-if="excelPreviewLoading" style="text-align: center; padding: 20px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p>正在解析Excel文件...</p>
      </div>
      <template v-else>
        <el-alert
          :title="`成功解析 ${excelPreviewPoints.length} 个点位`"
          type="success"
          :closable="false"
          show-icon
          style="margin-bottom: 12px"
        />
        <el-table :data="excelPreviewPoints" border size="small" max-height="350">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="name" label="点位名称" min-width="120" />
          <el-table-column prop="address" label="地址" min-width="140" />
          <el-table-column prop="type" label="数据类型" width="90" />
          <el-table-column prop="rate" label="倍率" width="70" />
          <el-table-column prop="offset" label="偏移" width="70" />
          <el-table-column prop="unit" label="单位" width="70" />
        </el-table>
        <p style="margin-top: 12px; font-size: 13px; color: #909399">
          确认后将自动打开添加设备对话框，点位已填入。
        </p>
      </template>
      <template #footer>
        <el-button @click="excelPreviewVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExcelImport" :disabled="excelPreviewLoading">
          确认并添加设备
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { ElMessage, ElMessageBox } from 'element-plus'

const devices = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const form = ref(getDefaultForm())

const testDialogVisible = ref(false)
const testing = ref(false)
const testResult = ref({ success: false, message: '' })

// Excel导入预览
const excelPreviewVisible = ref(false)
const excelPreviewLoading = ref(false)
const excelPreviewPoints = ref([])

// AI助手相关
const aiEnabled = ref(false)
const aiPanelActive = ref(['ai'])
const aiInput = ref('')
const aiStreaming = ref(false)
const aiStreamContent = ref('')
const aiPreview = ref(false)
const aiPreviewForm = ref(getDefaultForm())
const aiError = ref('')
const aiLastInput = ref('')  // 保存最后一次输入，用于重试
const aiExamples = [
  '帮我添加一台192.168.1.100的西门子S7-1200，采集DB3偏移0开始的10个浮点数，温度数据，单位℃',
  '添加一个Modbus TCP设备，IP是192.168.1.50，端口502，从站ID为1，采集保持寄存器40001到40010',
  '添加三菱FX5U PLC，IP 192.168.1.200，采集D100-D110的数据寄存器'
]

const protocolLabels = {
  modbus_tcp: 'Modbus TCP',
  modbus_rtu: 'Modbus RTU',
  s7: '西门子S7',
  mitsubishi: '三菱MC'
}

function getProtocolLabel(protocol) {
  return protocolLabels[protocol] || protocol
}

function getDefaultForm() {
  return {
    name: '',
    protocol: 'modbus_tcp',
    ip: '',
    port: null,
    com_port: '',
    baudrate: 9600,
    parity: 'N',
    databits: 8,
    stopbits: 1,
    slave_id: 1,
    rack: 0,
    slot: 1,
    plc_type: 'FX5U',
    enabled: true,
    points: []
  }
}

function onProtocolChange() {
  // 切换协议时重置端口默认值
  if (form.value.protocol === 'modbus_tcp') {
    form.value.port = 502
  } else if (form.value.protocol === 'mitsubishi') {
    form.value.port = 5000
  } else {
    form.value.port = null
  }
}

async function loadDevices() {
  try {
    const res = await axios.get('/api/devices')
    if (res.data.success) {
      devices.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('加载设备列表失败')
  }
}

function showAddDialog() {
  isEditing.value = false
  editingId.value = ''
  form.value = getDefaultForm()
  dialogVisible.value = true
}

function editDevice(device) {
  isEditing.value = true
  editingId.value = device.id
  form.value = JSON.parse(JSON.stringify(device))
  // RTU设备：port是串口号，映射到com_port
  if (form.value.protocol === 'modbus_rtu') {
    form.value.com_port = form.value.port || ''
  }
  dialogVisible.value = true
}

async function saveDevice() {
  // 生成ID
  if (!isEditing.value) {
    form.value.id = 'dev_' + Date.now()
  }

  // 处理端口字段：RTU用com_port覆盖port
  const data = { ...form.value }
  if (data.protocol === 'modbus_rtu') {
    data.port = data.com_port || data.port || 'COM1'
  }

  try {
    if (isEditing.value) {
      await axios.put(`/api/devices/${editingId.value}`, data)
      ElMessage.success('设备已更新')
    } else {
      await axios.post('/api/devices', data)
      ElMessage.success('设备已添加')
    }
    dialogVisible.value = false
    loadDevices()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.message || e.message))
  }
}

async function deleteDevice(device) {
  try {
    await ElMessageBox.confirm(`确定要删除设备 "${device.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await axios.delete(`/api/devices/${device.id}`)
    ElMessage.success('设备已删除')
    loadDevices()
  } catch (e) {
    if (e !== 'cancel' && e?.message !== 'cancel' && e !== 'close') {
      ElMessage.error('删除失败')
    }
  }
}

async function toggleDevice(device) {
  try {
    await axios.put(`/api/devices/${device.id}`, device)
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

async function testDevice(device) {
  testDialogVisible.value = true
  testing.value = true
  try {
    const res = await axios.post('/api/devices/test', { device })
    testResult.value = res.data
  } catch (e) {
    testResult.value = { success: false, message: '请求失败: ' + e.message }
  }
  testing.value = false
}

function addPoint() {
  form.value.points.push({
    name: '',
    address: '',
    type: 'float',
    rate: 1.0,
    offset: 0.0,
    unit: ''
  })
}

function removePoint(index) {
  form.value.points.splice(index, 1)
}

async function handleExcelImport(file) {
  const formData = new FormData()
  formData.append('file', file.raw)

  excelPreviewVisible.value = true
  excelPreviewLoading.value = true
  excelPreviewPoints.value = []

  try {
    const res = await axios.post('/api/devices/import-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data.success && res.data.data?.points) {
      excelPreviewPoints.value = res.data.data.points
    } else {
      ElMessage.warning(res.data.message || '导入失败')
      excelPreviewVisible.value = false
    }
  } catch (e) {
    ElMessage.error('导入失败: ' + (e.response?.data?.message || e.message))
    excelPreviewVisible.value = false
  }
  excelPreviewLoading.value = false
}

function confirmExcelImport() {
  const points = excelPreviewPoints.value
  if (points.length === 0) return

  // 打开添加设备对话框，填入导入的点位
  isEditing.value = false
  editingId.value = ''
  form.value = {
    ...getDefaultForm(),
    points: points.map(p => ({ ...p }))
  }
  excelPreviewVisible.value = false
  dialogVisible.value = true
  ElMessage.success(`已填入 ${points.length} 个点位，请完善设备信息后保存`)
}

function downloadTemplate() {
  const template = [
    ['点位名称', '地址', '数据类型', '倍率', '偏移', '单位'],
    ['温度1', 'DB1.DBD0', 'float', '1.0', '0', '℃'],
    ['压力1', 'DB1.DBD4', 'float', '1.0', '0', 'MPa'],
    ['运行状态', 'DB1.DBX8.0', 'bool', '1.0', '0', '-']
  ]

  const ws = XLSX.utils.aoa_to_sheet(template)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '点位表')
  XLSX.writeFile(wb, '点位表模板.xlsx')
  ElMessage.success('模板已下载')
}

// ==================== AI助手 ====================

async function loadAIConfig() {
  try {
    const res = await axios.get('/api/ai/config')
    if (res.data.success && res.data.data) {
      aiEnabled.value = res.data.data.enabled || false
    }
  } catch (e) {
    // 忽略
  }
}

async function aiParse() {
  const input = aiInput.value.trim()
  if (!input) return

  aiLastInput.value = input
  aiStreaming.value = true
  aiStreamContent.value = ''
  aiPreview.value = false
  aiError.value = ''
  aiInput.value = ''

  try {
    const response = await fetch('/api/ai/parse-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'chunk') {
              aiStreamContent.value += data.content
            } else if (data.type === 'done') {
              // 解析完成，展示可编辑预览
              aiPreviewForm.value = aiConfigToForm(data.config)
              aiPreview.value = true
              aiStreamContent.value = ''
            } else if (data.type === 'error') {
              aiError.value = data.message
            }
          } catch (e) {
            // 跳过解析失败的行
          }
        }
      }
    }
  } catch (e) {
    aiError.value = '请求失败: ' + e.message
  }
  aiStreaming.value = false
}

function aiConfigToForm(config) {
  return {
    name: config.name || '',
    protocol: config.protocol || 'modbus_tcp',
    ip: config.ip || '',
    port: config.port ?? null,
    slave_id: config.slave_id ?? 1,
    rack: config.rack ?? 0,
    slot: config.slot ?? 1,
    plc_type: config.plc_type || 'FX5U',
    com_port: config.com_port || '',
    baudrate: config.baudrate ?? 9600,
    parity: config.parity || 'N',
    databits: config.databits ?? 8,
    stopbits: config.stopbits ?? 1,
    enabled: config.enabled !== false,
    points: (config.points || []).map(p => ({
      name: p.name || '',
      address: p.address || '',
      type: p.type || 'float',
      rate: p.rate ?? 1.0,
      offset: p.offset ?? 0.0,
      unit: p.unit || ''
    }))
  }
}

function aiRetry() {
  aiInput.value = aiLastInput.value
  aiPreview.value = false
  aiStreamContent.value = ''
  aiError.value = ''
  aiParse()
}

function applyAIPreview() {
  const preview = aiPreviewForm.value
  form.value = {
    ...getDefaultForm(),
    name: preview.name,
    protocol: preview.protocol,
    ip: preview.ip,
    port: preview.port,
    slave_id: preview.slave_id,
    rack: preview.rack,
    slot: preview.slot,
    plc_type: preview.plc_type,
    com_port: preview.com_port,
    baudrate: preview.baudrate,
    parity: preview.parity,
    databits: preview.databits,
    stopbits: preview.stopbits,
    enabled: preview.enabled,
    points: preview.points.map(p => ({ ...p }))
  }

  if (form.value.protocol === 'modbus_rtu') {
    form.value.com_port = preview.com_port || ''
  }

  isEditing.value = false
  editingId.value = ''
  dialogVisible.value = true
  aiPreview.value = false
  aiStreamContent.value = ''
  ElMessage.success('AI配置已填入表单，请确认后保存')
}

onMounted(() => {
  loadDevices()
  loadAIConfig()
})
</script>

<style scoped>
.device-config-page {
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

.points-section {
  width: 100%;
}

/* AI助手面板 */
.ai-panel {
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fff;
}

.ai-panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.ai-chat-area {
  padding: 0 4px;
}

.ai-examples {
  margin-bottom: 12px;
}

.ai-examples-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.ai-example-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 10px;
  margin-bottom: 6px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  transition: all 0.2s;
}

.ai-example-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  color: #409eff;
}

.ai-example-icon {
  flex-shrink: 0;
  margin-top: 2px;
  color: #c0c4cc;
}

.ai-example-item:hover .ai-example-icon {
  color: #409eff;
}

/* 流式输出 */
.ai-streaming-box {
  margin-bottom: 12px;
  border: 1px solid #d9ecff;
  border-radius: 4px;
  background: #ecf5ff;
  overflow: hidden;
}

.ai-streaming-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #d9ecff;
  color: #409eff;
  font-size: 13px;
}

.ai-streaming-content {
  padding: 10px 12px;
  margin: 0;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* 可编辑预览卡片 */
.ai-preview-card {
  margin-bottom: 12px;
  border: 1px solid #b3e19d;
  border-radius: 6px;
  background: #f0f9eb;
  overflow: hidden;
}

.ai-preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #e1f3d8;
  font-size: 13px;
  color: #67c23a;
}

.ai-preview-header .el-button {
  margin-left: auto;
}

.ai-preview-form {
  padding: 12px 12px 0;
}

.ai-preview-points {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ai-preview-point-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ai-preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 12px 12px;
  border-top: 1px solid #e1f3d8;
  margin-top: 8px;
}

/* 错误提示 */
.ai-result-error {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
}

.ai-input-area {
  margin-top: 4px;
}
</style>
