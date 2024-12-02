<template>
    <div class="card" :class="{ selected: $props.selected }">
        <img :src="path" alt="card" width="100%" height="100%" />
        <div v-if="show" class="number-overlay">{{ number }}x</div>
    </div>
</template>

<script>
export default {
    name: 'Card',
    props: {
        path: String,
        show: {
            type: Boolean,
            default: false,
        },
        number: {
            type: Number,
            default: 1,
        },
        selected: {
            type: Boolean,
            default: false,
        },
    }
}
</script>

<style scoped>
.card {
    border: 1px solid #000;
    border-radius: 8px;
    width: 50px;
    height: 75px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    background-color: white;
    padding: 2px;
}

.card img {
    width: 100%;
    height: 100%;
}

.selected {
    border: 2px solid red;
}

.number-overlay {
    position: absolute;
    font-size: 24px;
    color: white;
    background-color: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    padding: 5px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
</style>