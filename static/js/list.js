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
                alert(data);
            },
            error: function(jqXHR, textStatus, errorThrown) 
            {
            }          
            });
            e.preventDefault(); //Prevent Default action. 
    });
});
