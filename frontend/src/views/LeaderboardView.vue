<template>
    <div class="bg-image"></div>
    <div class="container">
        <header>
            <h1 class="text-oldalcim">Leaderboard</h1>
        </header>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Felhasználónév</th>
                        <th>Pontszám</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="row in leaderboard" :key="row.user_id">
                        <td>{{ row.username }}</td>
                        <td>{{ row.score }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

onMounted(async () => {
    const response = await fetch('http://localhost:5000/leaderboard');
    const data = await response.json();
    leaderboard.value = data.leaderboard;
});

const leaderboard = ref([]);
</script>

<style scoped>
.bg-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('https://images.unsplash.com/photo-1646809014367-2c267bcba69f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
    background-size: cover;
    background-position: center;
    z-index: -1;
}

body {
    background-color: transparent;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.container {
    background-color: #ffffff;
    padding: 2rem;
    margin: 2rem auto;
    width: 90%;
    max-width: 800px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

header {
    background-color: #4CAF50;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
    border-radius: 8px 8px 0 0;
}

.text-oldalcim {
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
    margin: 0;
}

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 auto;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

th,
td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: center;
    vertical-align: middle;
    width: 50%;
}

th {
    background-color: #4CAF50;
    color: #ffffff;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #f2f2f2;
}

tr:hover {
    background-color: #e9e9e9;
}

tbody tr {
    transition: background-color 0.3s;
}

@media (max-width: 600px) {

    th,
    td {
        padding: 8px;
    }

    .text-oldalcim {
        font-size: 20px;
    }
}
</style>