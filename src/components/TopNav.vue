<template>
    <div class="container">
        <ul class="nav nav-fill justify-content-center">
            <li class="nav-item" v-for="(book, index) in this.books" :key="'book'+index">
                <router-link :to="`/reader/${index}`" class="nav-link" :class="dynamicClass(index)">{{ book.title }}</router-link>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    props: ['books', 'active'],
    methods: {
        dynamicClass(index) {
            return `${index == this.active ? "active" : ""} ${this.books[index].disabled ? "disabled" : ""}`
        }
    }
}
</script>

<style scoped>
.container {
    background-color: #8df;
    border-bottom: 3px solid #22b;
    padding-top: 10px;
}
.active {
    background-color: #22b;
    color: #fff;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
</style>