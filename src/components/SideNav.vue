<template>
    <div class="container justify-content-left">
        <router-link :to="`/reader/${bookNumber}`" class="book-title nav-link">
            <h3>{{ book.title }}</h3>
        </router-link>
        <div class="scroll-pane">
            <ul class="nav flex-column">
                <li class="nav-item" v-for="(chapter, index) in book.chapters" :key="'chapter'+index">
                    <router-link :to="`/reader/${bookNumber}/${index}`" class="nav-link" :class="dynamicClass(index)">{{ book.chapters[index].title }}</router-link>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    props: ['book', 'bookNumber', 'active'],
    methods: {
        dynamicClass(index) {
            return `${index == this.active ? "active" : "inactive"} ${this.book.chapters[index].disabled ? "disabled" : ""}`
        }
    }
}
</script>

<style scoped>
    .container {
        background-color: #22b;
        padding-top: 10px;
        color: #fff;
        border-bottom-left-radius: 30px;
    }
    .scroll-pane {
        margin-right: -15px;
        max-height: 70vh;
        overflow-x: hidden;
        overflow-y: scroll;
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* IE 10= */
    }
    .scroll-pane::-webkit-scrollbar { /* WebKit */
        width: 0;
        height: 0;
    }
    .active {
        background-color: #fff;
        color: #22b;
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
    }
    .inactive {
        color: #fff
    }
    .book-title {
        color: #fff
    }
</style>