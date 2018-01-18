var config = {
    motionPrefix: 'motion/',
    spriteFrames: 50
};

var MotionVideo = {
    template: '<video preload="none" :poster="poster" :controls="controls" :style="[styleSize, stylePos]" @click="play" @mousemove="slide" @touchmove="slide" @mouseleave="reset"><source :src="mp4" type="video/mp4"></video>',
    props: ['basename'],
    data: function() {
        var basename = this.basename;
        return {
            mp4: basename + '.mp4',
            jpg: basename + '.jpg',
            sprite: basename + '-sprite.jpg',

            poster: basename + '.jpg',
            controls: false,
            preview: false,
            styleSize: null,
            stylePos: null
        };
    },
    methods: {
        play: function(event) {
            if (this.controls) return;
            this.reset();
            event.currentTarget.play();
            this.controls = true;
        },
        slide: function(event) {
            if (this.controls) return;
            var rect = event.target.getBoundingClientRect();
            var clientX;
            if (event.touches) {
                clientX = event.touches[0].clientX;
            } else {
                clientX = event.clientX;
            }
            var left = clientX - rect.left;
            var width = rect.right - rect.left;
            var percent = left / width;
            if (percent >= 0.99) percent = 0.99;
            if (!this.preview) {
                if (percent < 0.2) {
                    var height = rect.bottom - rect.top;
                    this.preview = true;
                    this.poster = this.sprite;
                    this.styleSize = {
                        width: width + 'px',
                        height: height + 'px'
                    };
                }
            } else {
                this.stylePos = {
                    'object-position': '-' + Math.floor(percent * config.spriteFrames) * width + 'px'
                };
            }
        },
        reset: function() {
            if (this.controls) return;
            this.preview = false;
            this.poster = this.jpg;
            this.styleSize = null;
            this.stylePos = null;
        }
    }
};

var app = new Vue({
    el: '#app',
    template: '#app-template',
    components: {
        'flat-pickr': VueFlatpickr,
        'motion-video': MotionVideo
    },
    data: {
        videos: [],
        date: 'today'
    },
    computed: {
        videosFiltered: function() {
            var vm = this;
            return this.videos.filter(function(video) {
                var date = new Date(vm.date + ' 00:00:00');
                return video.date >= date && video.date <= date.fp_incr(1);
            });
        },
        dateConfig: function() {
            var minDate = null;
            var maxDate = null;
            if(this.videos.length > 0) {
                minDate = this.videos[0].date;
                maxDate = this.videos[this.videos.length - 1].date;
            }
            return {
                minDate: minDate,
                maxDate: maxDate
            };
        }
    },
    methods: {
        update: function() {
            var vm = this;
            axios.get(config.motionPrefix)
                .then(function(response) {
                    vm.videos = response.data
                        .filter(function(file) {
                            return file.name.endsWith('.jpg') && ! file.name.endsWith('-sprite.jpg');
                        })
                        .map(function(file) {
                            var m= file.name.match(/^(\d{4})-(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})\./);
                            var date = new Date(m[1]+'-'+m[2]+'-'+m[3]+' '+m[4]+':'+m[5]+':'+m[6]);
                            var basename = config.motionPrefix + file.name.replace(/\.jpg$/, '');
                            return {
                                basename: basename,
                                date: date
                            };
                        });
                });
        }
    },
    created: function() {
        this.update();
    }
});
