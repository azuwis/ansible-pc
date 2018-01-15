var motion_prefix = 'motion/';

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
            axios.get(motion_prefix)
                .then(function(response) {
                    vm.videos = response.data
                        .filter(function(file) {
                            return file.name.endsWith('.jpg');
                        })
                        .map(function(file) {
                            var m= file.name.match(/^(\d{4})-(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})\./);
                            var date = new Date(m[1]+'-'+m[2]+'-'+m[3]+' '+m[4]+':'+m[5]+':'+m[6]);
                            return {
                                source: motion_prefix + file.name.replace(/\.jpg$/, '.mp4'),
                                poster: motion_prefix + file.name,
                                date: date,
                                controls: false
                            };
                        });
                });
        },
        play: function(video, event) {
            video.controls = true;
            event.currentTarget.play();
        }
    },
    created: function() {
        this.update();
    }
});
