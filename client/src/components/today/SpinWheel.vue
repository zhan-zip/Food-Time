<template>
  <div class="spin-wheel-wrapper">
    <!-- 指针 -->
    <div class="spin-pointer">&#x25BC;</div>

    <!-- Canvas 转盘（外层固定 CSS 尺寸） -->
    <div class="spin-canvas-box">
      <canvas
        ref="canvasRef"
        class="spin-canvas"
      ></canvas>

      <!-- 中心按钮 -->
      <button
        class="spin-center-btn"
        :disabled="spinning || items.length < 2"
        @click="spin"
      >
        {{ spinning ? '...' : 'GO' }}
      </button>
    </div>

    <!-- 结果 -->
    <div v-if="result && !spinning" class="spin-result">
      <span class="spin-result-icon">&#x1F389;</span>
      {{ result.label }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const emit = defineEmits(['done'])

const canvasRef = ref(null)
const CSS_SIZE = 280 // CSS 显示尺寸
const DPR = Math.min(window.devicePixelRatio || 1, 2) // 设备像素比，限制最大 2x 避免性能问题
const CANVAS_SIZE = CSS_SIZE * DPR // 物理像素尺寸（高 DPI 屏下保证转盘文字清晰不模糊）

const spinning = ref(false)
const result = ref(null)
const currentRotation = ref(0)

const COLORS = [
  '#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6',
  '#1ABC9C', '#E67E22', '#2980B9', '#27AE60', '#D35400',
  '#8E44AD', '#16A085', '#C0392B', '#2C3E50', '#F1C40F',
]

function drawWheel() {
  const canvas = canvasRef.value
  if (!canvas || !props.items.length) return
  const ctx = canvas.getContext('2d')

  // 设置 canvas 物理像素
  canvas.width = CANVAS_SIZE
  canvas.height = CANVAS_SIZE

  // 缩放上下文以匹配 DPR
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0)

  const cx = CSS_SIZE / 2
  const cy = CSS_SIZE / 2
  const r = CSS_SIZE / 2 - 4

  ctx.clearRect(0, 0, CSS_SIZE, CSS_SIZE)

  const n = props.items.length
  const sliceAngle = (2 * Math.PI) / n

  props.items.forEach((item, i) => {
    const startAngle = i * sliceAngle - Math.PI / 2
    const endAngle = startAngle + sliceAngle

    // 扇形
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.arc(cx, cy, r, startAngle, endAngle)
    ctx.closePath()
    ctx.fillStyle = item.color || COLORS[i % COLORS.length]
    ctx.fill()
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 1.5
    ctx.stroke()

    // 文字
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(startAngle + sliceAngle / 2)
    ctx.textAlign = 'right'
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 13px sans-serif'
    const label = item.label.length > 5 ? item.label.slice(0, 5) + '..' : item.label
    ctx.fillText(label, r - 16, 5)
    ctx.restore()
  })

  // 中心圆
  ctx.beginPath()
  ctx.arc(cx, cy, 26, 0, 2 * Math.PI)
  ctx.fillStyle = '#fff'
  ctx.fill()
  ctx.strokeStyle = '#E0D5C7'
  ctx.lineWidth = 2
  ctx.stroke()
}

function spin() {
  if (spinning.value || props.items.length < 2) return
  spinning.value = true
  result.value = null

  const n = props.items.length
  const sliceAngle = 360 / n
  const targetIdx = Math.floor(Math.random() * n)

  // 计算目标停止位置：让第 targetIdx 片的中心对准顶部指针
  // 片的中心角度（CW 从顶部起）= targetIdx * sliceAngle + sliceAngle/2
  // CSS rotate 顺时针 → 需要旋转量 = 360 - 中心角度（即反向旋转到顶部）
  const targetStop = ((360 - targetIdx * sliceAngle - sliceAngle / 2) % 360 + 360) % 360

  // 从当前位置到目标的增量（至少转 5 圈）
  const currentMod = ((currentRotation.value % 360) + 360) % 360
  let delta = ((targetStop - currentMod) % 360 + 360) % 360
  delta += 360 * 5

  // 微小抖动避免每次都停正中间
  const jitter = (Math.random() - 0.5) * sliceAngle * 0.7
  const targetAngle = currentRotation.value + delta + jitter

  const canvas = canvasRef.value
  canvas.style.transition = 'transform 4s cubic-bezier(0.2, 0.8, 0.3, 1)'
  canvas.style.transform = `rotate(${targetAngle}deg)`
  currentRotation.value = targetAngle

  spinTimer = setTimeout(() => {
    if (isUnmounted) return  // 修复 M4：组件已卸载则不再 emit
    spinning.value = false
    result.value = props.items[targetIdx]
    emit('done', props.items[targetIdx])
  }, 4200)
}

watch(() => props.items, () => {
  nextTick(drawWheel)
}, { deep: true })

onMounted(() => {
  drawWheel()
})

// 修复 M4：组件卸载时清理旋转定时器，防止 emit 到已卸载组件（Vue 警告/内存泄漏）
let spinTimer = null
let isUnmounted = false
onBeforeUnmount(() => {
  isUnmounted = true
  if (spinTimer) clearTimeout(spinTimer)
})
</script>

<style scoped>
.spin-wheel-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.spin-pointer {
  font-size: 24px;
  color: var(--color-primary-dark);
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
  margin-bottom: -2px;
  z-index: 3;
}

.spin-canvas-box {
  position: relative;
  width: 280px;
  height: 280px;
}

.spin-canvas {
  width: 280px;
  height: 280px;
  border-radius: 50%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  will-change: transform;
}

.spin-center-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  border: 3px solid #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spin-center-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.spin-center-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-result {
  margin-top: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}

.spin-result-icon {
  margin-right: 4px;
}
</style>
