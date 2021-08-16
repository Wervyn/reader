<template>
    <div class="container">
        <ul class="nav nav-fill justify-content-center">
            <li class="nav-item chapter-count">
                {{ index >= 0 ? index + 1 : "--" }} / {{ max+1 }}
            </li>
            <li class="nav-item">
                <router-link :to="`/reader/${book}/0`" class="nav-link" :class="lowerBound()">▌◀</router-link>
            </li>
            <li class="nav-item">
                <router-link :to="`/reader/${book}/${+index-1}`" class="nav-link" :class="lowerBound()">◀</router-link>
            </li>
            <li class="nav-item">
                <router-link :to="`/reader/${book}/${+index+1}`" class="nav-link" :class="upperBound()">▶</router-link>
            </li>
            <li class="nav-item">
                <router-link :to="`/reader/${book}/${max}`" class="nav-link" :class="upperBound()">▶▐</router-link>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    props: ['book', 'index', 'max'],
    methods: {
        lowerBound() {
            return this.index <= 0 ? "disabled" : "";
        },
        upperBound() {
            return this.index >= this.max ? "disabled" : "";
        }
    }
}
</script>

<style scoped>
    .container {
        width: 100%;
        background-color: #22b;
        border-bottom-right-radius: 30px;
    }
    .nav-link {
        color: #fff;
    }
    .disabled {
        color: #777;
    }
    .chapter-count {
        color: #fff;
        background-color: #44c;
        display: flex;
        align-content: center;
        justify-content: center;
        flex-direction: column;
        font-weight: bold;
    }
</style>