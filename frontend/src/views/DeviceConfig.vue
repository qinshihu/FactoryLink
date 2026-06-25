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

function handleExcelImport(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheet = workbook.Sheets[workbook.SheetNames[0]]
      const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 })

      if (rows.length < 2) {
        ElMessage.warning('Excel文件为空')
        return
      }

      // 第一行为表头，跳过
      const points = []
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i]
        if (!row || row.length < 3) continue
        points.push({
          name: String(row[0] || ''),
          address: String(row[1] || ''),
          type: String(row[2] || 'float'),
          rate: parseFloat(row[3]) || 1.0,
          offset: parseFloat(row[4]) || 0.0,
          unit: String(row[5] || '')
        })
      }

      if (points.length === 0) {
        ElMessage.warning('未解析到有效点位数据')
        return
      }

      // 将导入的点位添加到当前编辑的设备
      form.value.points = [...form.value.points, ...points]
      ElMessage.success(`成功导入 ${points.length} 个点位`)
    } catch (err) {
      ElMessage.error('Excel解析失败: ' + err.message)
    }
  }
  reader.readAsArrayBuffer(file.raw)
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

onMounted(() => {
  loadDevices()
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
</style>
