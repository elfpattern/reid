var app = new Vue({
    el:'#app',
    data: {
        img1:[],
        img2:[],
        loading: false,
    },
    methods: {
        Begin: function(){
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/begin',
                type:'post',
                dataType:'json',
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }

            })

        },
        Merge: function(){
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/yes', //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            });
        },
        Split: function(){
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/no',  //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            })
        },
        FPL: function(){
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/fpl',  //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            })
        },
        FPR: function(){
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/fpr',  //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            })
        },
        FPA: function(){
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/fpa',  //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            })
        },
        Save: function() {
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/save',  //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            })
        },
        Reset: function() {
            var x = this;
            this.loading=true;
            $.ajax({
                url:'/reset',  //服务器地址
                type:'post',//type是ajax的方法，可以用post也可以用get
                dataType:'json',//传递的数据类型，可以是json
                success:function(data){
                    x.img1 = data.img1;
                    x.img2 = data.img2;
                    x.loading=false;
                },
                error:function(error){
                    console.log(error);
                    x.loading=false;
                }
            })
        }
    }});
