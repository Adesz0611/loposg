<template>
    <div>
            <BCointainer>
            <BRow>
                <BCol>
                    <BCard>
                        <BCardHeader class="text-center">
                            <h1 class="text-primary">Ranglista</h1>
                        </BCardHeader>
                        <BCardBody>
                            <b-table striped hover>
                                <thead>
                                    <tr>
                                        <th>Helyezés</th>
                                        <th>Felhasználónév</th>
                                        <th>Pontszám</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>1.</td>
                                        <td>John Doe</td>
                                        <td>100</td>
                                    </tr>
                                    <tr>
                                        <td>2.</td>
                                        <td>Jane Doe</td>
                                        <td>90</td>
                                    </tr>
                                    <tr>
                                        <td>3.</td>
                                        <td>Jack Doe</td>
                                        <td>80</td>
                                    </tr>
                                </tbody>
                            </b-table>
                        </BCardBody>
                    </BCard>
                </BCol>
            </BRow>
        </BCointainer>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoomIdStore } from '../stores/room_id';
import { createRouter, useRouter } from 'vue-router';
const router = useRouter();

const roomIdStore = useRoomIdStore();
const userName = ref('John Doe');
const userEmail = ref('john.doe@example.com');

function goToHome() {
    router.push('/');
}

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