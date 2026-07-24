import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getDIYIngredients, suggestRecipe, saveRecipe, getMyRecipes } from '@/api/diy'

export const useDIYStore = defineStore('diy', () => {
  // ---- 食材数据 ----
  const fridgeLeft = ref([])    // 冰箱左门 [{key, label, color, items}]
  const fridgeRight = ref([])   // 冰箱右门
  const seasoning = ref({})     // 调料台
  const loading = ref(false)

  // ---- 冰箱状态 ----
  const fridgeOpen = ref(false)

  // ---- 已选食材 ----
  const plate = ref([])         // [{name, emoji, type:'ingredient'|'seasoning'}]
  const MAX_PLATE = 12

  // ---- 烹饪阶段 ----
  // selecting → suggesting → cooking → saving → done
  const stage = ref('selecting')

  // ---- AI 建议 ----
  const matchedRecipes = ref([])  // 数据库匹配到的菜谱
  const aiSuggestion = ref(null)  // AI 生成的建议
  const suggestionSource = ref('') // 'database' | 'ai' | 'fallback' | 'error'
  const suggestError = ref('')

  // ---- 烹饪方式 ----
  const cookingMethod = ref('wok') // 'wok' | 'air_fryer' | 'steamer'
  const cookingMethods = [
    { key: 'wok', label: '🍳 炒锅', desc: '大火快炒' },
    { key: 'air_fryer', label: '🔥 空气炸锅', desc: '低油健康' },
    { key: 'steamer', label: '♨️ 蒸锅', desc: '原汁原味' },
  ]
  const showAnimation = ref(false)
  const animationPlaying = ref(false)

  // ---- 保存 ----
  const showSaveDialog = ref(false)
  const lastSavedRecipe = ref(null)

  // ---- 我的菜谱 ----
  const myRecipes = ref([])

  // ---- 计算属性 ----
  const ingredientNames = computed(() =>
    plate.value.filter(p => p.type === 'ingredient').map(p => p.name)
  )
  const seasoningNames = computed(() =>
    plate.value.filter(p => p.type === 'seasoning').map(p => p.name)
  )
  const plateCount = computed(() => plate.value.length)
  const canSuggest = computed(() => plateCount.value > 0 && stage.value === 'selecting')
  const hasMatchedRecipes = computed(() => matchedRecipes.value.length > 0)

  // ---- 食材操作 ----
  function addToPlate(item, type = 'ingredient') {
    if (plate.value.length >= MAX_PLATE) return false
    if (plate.value.some(p => p.name === item.name && p.type === type)) return false
    plate.value.push({ ...item, type })
    return true
  }

  function removeFromPlate(index) {
    plate.value.splice(index, 1)
  }

  function clearPlate() {
    plate.value = []
    matchedRecipes.value = []
    aiSuggestion.value = null
    suggestionSource.value = ''
    suggestError.value = ''
    stage.value = 'selecting'
    showAnimation.value = false
    animationPlaying.value = false
  }

  // ---- API 调用 ----
  async function loadIngredients() {
    loading.value = true
    try {
      const res = await getDIYIngredients()
      fridgeLeft.value = res.fridge.left
      fridgeRight.value = res.fridge.right
      seasoning.value = res.seasoning
    } catch (e) {
      console.error('加载食材失败', e?.message || e)
    } finally {
      loading.value = false
    }
  }

  async function fetchSuggestion() {
    if (!canSuggest.value) return
    stage.value = 'suggesting'
    suggestError.value = ''
    matchedRecipes.value = []
    aiSuggestion.value = null

    try {
      const res = await suggestRecipe({
        ingredients: ingredientNames.value,
        seasonings: seasoningNames.value,
      })

      if (res.matched && res.matched.length > 0) {
        matchedRecipes.value = res.matched.slice(0, 5)
        suggestionSource.value = 'database'
      }

      if (res.ai_suggestion) {
        aiSuggestion.value = res.ai_suggestion
        suggestionSource.value = res.source || 'ai'
        cookingMethod.value = res.ai_suggestion.cooking_method || 'wok'
      }

      if (res.error) {
        const e = res.error
        suggestError.value = typeof e === 'object' ? (e.msg || e.message || JSON.stringify(e)) : String(e)
      }
    } catch (e) {
      suggestError.value = e?.message || '获取建议失败'
      stage.value = 'selecting'
    }
  }

  function startCooking() {
    stage.value = 'cooking'
    showAnimation.value = true
    animationPlaying.value = true
  }

  function skipAnimation() {
    showAnimation.value = false
    animationPlaying.value = false
    stage.value = 'saving'
  }

  function onAnimationDone() {
    animationPlaying.value = false
  }

  function openSaveDialog() {
    showSaveDialog.value = true
  }

  async function doSave({ name, description, publishToSquare }) {
    try {
      const res = await saveRecipe({
        name,
        description: description || null,
        ingredients: ingredientNames.value,
        seasonings: seasoningNames.value,
        cooking_method: cookingMethod.value,
        cooking_steps: aiSuggestion.value?.steps || [],
        estimated_calories: aiSuggestion.value?.estimated_calories || null,
        publish_to_square: publishToSquare,
      })
      lastSavedRecipe.value = res
      showSaveDialog.value = false
      stage.value = 'done'
      return res
    } catch (e) {
      return { success: false, message: e?.response?.data?.detail || '保存失败' }
    }
  }

  async function loadMyRecipes() {
    try {
      const res = await getMyRecipes()
      myRecipes.value = res.items
    } catch (e) {
      console.error('加载我的菜谱失败', e)
    }
  }

  return {
    // state
    fridgeLeft, fridgeRight, seasoning, loading,
    fridgeOpen, plate, MAX_PLATE,
    stage, matchedRecipes, aiSuggestion, suggestionSource, suggestError,
    cookingMethod, cookingMethods, showAnimation, animationPlaying,
    showSaveDialog, lastSavedRecipe, myRecipes,
    // computed
    ingredientNames, seasoningNames, plateCount, canSuggest, hasMatchedRecipes,
    // actions
    addToPlate, removeFromPlate, clearPlate,
    loadIngredients, fetchSuggestion,
    startCooking, skipAnimation, onAnimationDone,
    openSaveDialog, doSave, loadMyRecipes,
  }
})
