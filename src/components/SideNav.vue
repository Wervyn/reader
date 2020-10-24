<template>
    <div class="container justify-content-left">
        <div><router-link :to="`/reader/${bookNumber}`" class="book-title nav-link" ref="titleLink">
            <h3>{{ book.title }}</h3>
        </router-link></div>
        <div class="scroll-pane" :style="{'max-height': `calc(100% - 20px - ${titleHeight}px)`}" ref="sidebarContent" @scroll="setScroll()">
            <ul class="nav flex-column">
                <li class="nav-item" v-for="index in listChapters()" :key="'chapter'+index">
                    <router-link :id="'chapter-'+index" :to="`/reader/${bookNumber}/${index}`" class="nav-link"
                        :class="dynamicClass(index)">
                        {{ book.chapters[index].title }}
                    </router-link>
                </li>
            </ul>
            <div class="scrollbar" :style="dynamicScrollbar()"></div>
        </div>
    </div>
</template>

<script>
export default {
    props: ['book', 'bookNumber', 'active'],
    data() { return {
        titleHeight: 100,
        offsetHeight: 600,
        scrollHeight: 600,
        scrollTop: 0,
    }},
    methods: {
        dynamicClass(index) {
            return `${index == this.active ? "active" : "inactive"} 
                    ${this.book.chapters[index].disabled ? "disabled" : ""} 
                    ${localStorage.getItem("isDark") ? "dark" : ""}`
        },
        listChapters() {
            let range = this.book.chapters ? Array.from(this.book.chapters.keys()) : [];
            if (this.book.reverse) range.reverse();
            return range;
        },
        setTitleHeight() {
            this.titleHeight = this.$refs.titleLink.$el.offsetHeight;
            this.setScroll();
        },
        setScroll() {
            this.offsetHeight = this.$refs.sidebarContent.offsetHeight;
            this.scrollHeight = this.$refs.sidebarContent.scrollHeight;
            this.scrollTop = this.$refs.sidebarContent.scrollTop;
        },
        scrollTo(index) {
            this.setScroll();
            if (window.innerWidth <= 575) return;
            var el = document.querySelector(`#chapter-${index}`);
            el.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        },
        dynamicScrollbar() {
            if (this.offsetHeight >= this.scrollHeight) {
                return {'display': 'none'};
            }
            return {
                'height': `${Math.trunc(this.offsetHeight * this.offsetHeight / this.scrollHeight)}px`,
                'top': `${Math.trunc(this.titleHeight + this.scrollTop * this.offsetHeight / this.scrollHeight + 10)}px`
            };
        }
    },
    mounted() {
        window.addEventListener('resize', this.setTitleHeight);
        setTimeout(this.setTitleHeight, 500);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.setTitleHeight);
    }
}
</script>

<style scoped>
    .container {
        background-color: #22b;
        padding-top: 10px;
        color: #fff;
        border-bottom-left-radius: 30px;
        height: 100%;
        min-height: 100%;
        max-height: 100%;
    }
    .scroll-pane {
        margin-right: -15px;
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
    .active.dark {
        background-color: #333;
        color: #fff;
        /*color: #be9d3c;*/
    }
    .inactive {
        color: #fff;
    }
    .book-title {
        color: #fff;
    }
    .scrollbar {
        position: absolute;
        left: 10px;
        z-index: 5;
        background-color: #8df;
        opacity: .5;
        width: 10px;
        border-radius: 5px;
    }
</style>