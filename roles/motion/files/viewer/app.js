var config = {
    motion_prefix: 'motion/',
    preview_frames: 50
};

Vue.component('flat-pickr', VueFlatpickr);

var app = new Vue({
    el: '#app',
    template: '#app-template',
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
            axios.get(config.motion_prefix)
                .then(function(response) {
                    vm.videos = response.data
                        .filter(function(file) {
                            return file.name.endsWith('.jpg') && ! file.name.endsWith('-preview.jpg');
                        })
                        .map(function(file) {
                            var m= file.name.match(/^(\d{4})-(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})\./);
                            var date = new Date(m[1]+'-'+m[2]+'-'+m[3]+' '+m[4]+':'+m[5]+':'+m[6]);
                            var basename = config.motion_prefix + file.name.replace(/\.jpg$/, '');
                            return {
                                source: basename + '.mp4',
                                img: basename + '.jpg',
                                poster: basename + '.jpg',
                                preview: basename + '-preview.jpg',
                                date: date,
                                play: false,
                                previewEnabled: false,
                                style: null
                            };
                        });
                });
        },
        play: function(video, event) {
            this.disablePreview(video);
            event.currentTarget.play();
            video.play = true;
        },
        slidePreview: function(video, event) {
            if (video.play) return;
            var rect = event.target.getBoundingClientRect();
            var left = event.pageX - rect.left;
            var width = rect.right - rect.left;
            var percent = left / width;
            if (percent > 0.2 && !video.previewEnabled) return;
            video.previewEnabled = true;
            video.img = null;
            video.style = {
                'background-image': 'url(' + video.preview + ')',
                'background-position': '-' + Math.floor(percent * config.preview_frames) * width + 'px'
            };
        },
        disablePreview: function(video) {
            if (video.play) return;
            video.img = video.poster;
            video.style = null;
        }
    },
    created: function() {
        this.update();
    }
});
