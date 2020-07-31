$(document).ready(function () {
    let target = $("#fileDrag, #imageDrag")
    let inputTarget = $("#id_image, #id_file")


    $(document.body).bind('drop', function (e) {
        e.preventDefault();
    });

    target.bind('dragover', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragging');
    });

    target.bind('dragexit', function (e) {
        $(this).removeClass('dragging');

    });

    target.bind('dragleave', function (e) {
        e.preventDefault();
        $(this).removeClass('dragging');
    });

    target.bind('drop', function (e) {
        e.preventDefault();
        e.stopPropagation();
        let fileTypes = null, tag = null, fileInput = null;
        if (e.target.id === "fileDrag") {
            tag = "Files"
            fileInput = document.querySelector('input#id_file');
            fileTypes = ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar',]
        } else {
            tag = "Images"
            fileInput = document.querySelector('input#id_image');
            fileTypes = ['png', 'jpg', 'jpeg', 'PNG', 'JPG']
        }
        $(this).children('#alertPop').remove()
        $(this).removeClass('dragging');
        $(this).parent().children('div').remove();

        fileInput.files = e.originalEvent.dataTransfer.files;

        let files = e.originalEvent.dataTransfer.files,
            filesLength = files.length;
        for (let i = 0; i < filesLength; i++) {
            let extension = files[i].name.split('.').pop().toLowerCase(),  //file extension from input file
                isSuccess = fileTypes.indexOf(extension) > -1,  //is extension in acceptable types
                f = files[i];
            if (!(isSuccess)) {
                $(this).append(`<br><span id="alertPop" class='alert-danger text-danger'>One of the files you trying to upload is not supported as ${tag}</span>`)
                fileInput.value = ""
                return
            }
            let append_Area = $(this).parent().children('.previewArea')
            if (e.target.id === "fileDrag") {
                $(` <div class="file-preview row justify-content-center">
                        <div class="col-2">
                            <img style="width: 75px;height: 75px;" src="/static/images/file_ex_icon/${extension}.png" alt="" />
                        </div>
                        <div class="col-3">
                            <span class="float-left">${files[i].name}</span>
                        </div>
                    </div>
                `).insertAfter(append_Area);
            } else {
                let fileReader = new FileReader();
                fileReader.onload = (function (e) {
                    let file = e.target;
                    $(` <div class="file-preview d-inline-block mx-3">
                                <img style="width: 75px;height: 75px;" src="${file.result}" alt="" />
                        </div>
                    `).insertAfter(append_Area);

                });
                fileReader.readAsDataURL(f);

            }
        }

    });

    inputTarget.on('change', function(e){
        if (e.target.id === "id_file") {
            tag = "Files"
            fileInput = document.querySelector('input#id_file');
            fileTypes = ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar',]
        } else {
            tag = "Images"
            fileInput = document.querySelector('input#id_image');
            fileTypes = ['png', 'jpg', 'jpeg', 'PNG', 'JPG']
        }

        console.log($(this).parent().parent())
        $(this).parent().children('#alertPop').remove()
        $(this).parent().removeClass('dragging');
        $(this).parent().parent().children('div').remove();
        let files = this.files,
            filesLength = files.length;
        console.log(files)
        for (let i = 0; i < filesLength; i++) {
            let extension = files[i].name.split('.').pop().toLowerCase(),  //file extension from input file
                isSuccess = fileTypes.indexOf(extension) > -1,  //is extension in acceptable types
                f = files[i];
            if (!(isSuccess)) {
                $(this).parent().append(`<br><span id="alertPop" class='alert-danger text-danger'>One of the files you trying to upload is not supported as ${tag}</span>`)
                fileInput.value = ""
                return
            }
            let append_Area = $(this).parent().parent().children('.previewArea')
            if (e.target.id === "id_file") {
                $(` <div class="file-preview row justify-content-center">
                        <div class="col-2">
                            <img style="width: 75px;height: 75px;" src="/static/images/file_ex_icon/${extension}.png" alt="" />
                        </div>
                        <div class="col-3">
                            <span class="float-left">${files[i].name}</span>
                        </div>
                    </div>
                `).insertAfter(append_Area);
            } else {
                let fileReader = new FileReader();
                fileReader.onload = (function (e) {
                    let file = e.target;
                    $(` <div class="file-preview d-inline-block mx-3">
                                <img style="width: 75px;height: 75px;" src="${file.result}" alt="" />
                        </div>
                    `).insertAfter(append_Area);

                });
                fileReader.readAsDataURL(f);

            }
        }

    })
});


