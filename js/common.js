$(document).ready(function() {
    $(document).foundationCustomForms();
    //$(document).foundationNavigation();

    $("#content-edit-form div.content-edit").hallo({
        plugins: {
            "halloformat": {
                "formattings": {
                    "bold": true,
                    "italic": true,
                    "underline": true,
                    "strikethrough": true,
                }
            }
        },
        toolbar: "halloToolbarContextual"
    });

    $("#content-edit-form").submit(function(e) {
        var th = $(this);
        var wrapper = th.find("div.content-edit-wrapper");
        var hidden = wrapper.find("#hidden");
        hidden.val(wrapper.find("div.content-edit").html());
    });
});
