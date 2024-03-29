$(document).ready(function(){
    $( "#addAuction" ).click(function() {
        url = $("#inputURL")[0].value
        bottomPrice = $("#inputBottomPrice")[0].value

        $("#auctionTable > tbody:last").append(
            "<tr><td class='url'>"+url+"</td><td class='bottomPrice'>"+bottomPrice+"</td><td>删除</td>"
        )
    });

    $("#submitData").click(function(){
        var auction_list = []
        urls = $(".url")                     
        bottomPrices = $(".bottomPrice")
        $.each(urls,function(n,value) {
            var auction_dict = {}
            auction_dict['url'] = value.innerHTML
            auction_dict['bottomPrice'] = bottomPrices[n].innerHTML
            auction_list.push(auction_dict)
        });
        var parameters = {
            "auction_list": JSON.stringify(auction_list)
        }
        $.post("/list", data=parameters) 

    })

    $("#updateGapLevel").click(function(){
        var gap_dict = {"gap_level1":"0"}
        gap_dict["gap_level1"] = $("#gap_level1")[0].value
        param = {'gap_dict': JSON.stringify(gap_dict)}
        $.post("/gap_level", data=param, function(ret_data){
        gl1 = ret_data['gap_level1']
        $("#gap_level1").val(gl1)
        })
    })
 
    $.get("/gap_level", function( data ) {
        gl1 = data['gap_level1']
        $("#gap_level1").val(gl1)
    });

    $("#deleteBtn").click(function(){
        $.post("/delete", function(){
            location.reload()
        });
        
    })
        
    $("#fileForm").submit(function(e){
    
        var formObj = $(this);
        var formURL = formObj.attr("action");
        var formData = new FormData(this);
        $.ajax({
            url: formURL,
            type: 'POST',
            data:  formData,
            mimeType:"multipart/form-data",
            contentType: false,
            cache: false,
            processData:false,
            success: function(data, textStatus, jqXHR)
            {
                obj = JSON.parse(data);
                if (obj.error == -1)
                    alert("文件格式错误!")
                else
                    alert("上传成功,回到首页查看")
            },
            error: function(jqXHR, textStatus, errorThrown) 
            {
            }          
            });
            e.preventDefault(); //Prevent Default action. 
    });
});
