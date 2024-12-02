<template>
    <table>
        <thead>
            <tr>
                <th>Felhasználónév</th>
                <th>Pontszám</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="row in leaderboard" :key="row.username">
                <td>{{ row.username }}</td>
                <td>{{ row.score }}</td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
import { ref } from 'vue';

const leaderboard = ref([
    { username: 'Lencse', score: 100 },
    { username: 'Jampy', score: 90 },
    { username: 'Dr. Momó', score: 80 },
    { username: 'Leslie', score: 70 },
    { username: 'Geckó', score: 60 },
]);

</script>

<style scoped>
header {
    background-color: #f8f9fa;
    padding: 1rem;
    text-align: center;
}

h1 {
    margin: 0;
    font-size: 1.5rem;
}
</style>