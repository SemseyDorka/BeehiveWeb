<template>
  <div class="container mt-5">
    <h1 class="mb-4 text-center text-success"> Kaptár Mérleg </h1>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-success" role="status"></div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else class="card shadow">
      <div class="card-body">
        <table class="table table-striped table-hover">
          <thead class="table-success">
            <tr>
              <th>Kaptár</th>
              <th>Súly (kg)</th>
              <th>Külső Hőfok</th>
              <th>Fészek Hőfok</th>
              <th>Időpont</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sor in meresek" :key="sor.id">
              <td><span class="badge bg-secondary">#{{ sor.kaptar }}</span></td>
              <td class="fw-bold">{{ sor.suly }} kg</td>
              <td>{{ sor.homerseklet }} °C</td>
              <td>{{ sor.feszek_homerseklet }} °C</td>
              <td class="text-muted">{{ sor.datum }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  setup() {
    const meresek = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchAdatok = async () => {
      try {
        const response = await fetch('/api/meresek')
        if (!response.ok) throw new Error('Nem sikerült elérni a szervert.')
        meresek.value = await response.json()
      } catch (err) {
        error.value = 'Hiba történt: ' + err.message
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchAdatok)

    return { meresek, loading, error }
  }
}
</script>