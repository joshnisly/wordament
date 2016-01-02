function Board(parentElem, letters)
{
    this._cells = parentElem.find('TD');
    this._letters = '';
    for (var i = 0; i < letters.length; i++)
        this.onLetter(letters[i]);

    this._parentElem = parentElem;
}

Board.prototype.onLetter = function(letter)
{
    if (this.isFilled())
        return;

    $(this._cells[this._letters.length]).text(letter.toUpperCase());
    this._letters += letter;
};

Board.prototype.isFilled = function()
{
    return this._letters.length == this._cells.length;
};

Board.prototype.getLetters = function()
{
    return this._letters;
};

Board.prototype.drawWord = function(word)
{
    $('.Selected').removeClass('Selected');
    $('.Line').remove();

    var offset = [
        this._parentElem[0].offsetLeft,
        this._parentElem[0].offsetTop
    ];

    var coords = word[1];
    var lastCenter = null;
    for (var i = 0; i < coords.length; i++)
    {
        var cellIndex = coords[i][0] * 4 + coords[i][1];
        var cell = this._cells[cellIndex]

        $(cell).addClass('Selected');

        // Draw line between cells
        var center = [
            cell.offsetLeft + offset[0] + cell.offsetWidth / 2,
            cell.offsetTop + offset[1] + cell.offsetHeight / 2
        ]

        if (lastCenter)
            createLine(this._parentElem, lastCenter, center);

        lastCenter = center;
    }
};

function createLineElement(parent, x, y, length, angle)
{
    var line = $(parent).appendNewChild('DIV', '', 'Line');
    line.css({
        'border': '1px solid black',
        'width': length + 'px',
        'height': '0px',
        '-moz-transform': 'rotate(' + angle + 'rad)',
        '-webkit-transform': 'rotate(' + angle + 'rad)',
        '-o-transform': 'rotate(' + angle + 'rad)',
        '-ms-transform': 'rotate(' + angle + 'rad)',
        'position': 'absolute',
        'top': y + 'px',
        'left': x + 'px',
    });
    return line;
}

function createLine(parent, start, end)
{
    var x1 = start[0];
    var y1 = start[1];
    var x2 = end[0];
    var y2 = end[1];

    var a = x1 - x2,
        b = y1 - y2,
        c = Math.sqrt(a * a + b * b);

    var sx = (x1 + x2) / 2,
        sy = (y1 + y2) / 2;

    var x = sx - c / 2,
        y = sy;

    var alpha = Math.PI - Math.atan2(-b, a);

    createLineElement(parent, x, y, c, alpha);
}


function displayResults(results, board)
{
    var parentElem = $('#ResultsSection');
    for (var i = 0; i < results.length; i++)
    {
        var child = parentElem.appendNewChild('DIV', '', 'Result').text(results[i][0]);
        child[0].xresult = results[i];
        function selectWord(event)
        {
            board.drawWord(event.target.xresult);
            $(event.target).addClass('Selected');
        }
        child.bind('click', selectWord);
    }
}

function solve(letters, board)
{
    doAjax({
        url: '/solve/',
        method: 'POST',
        data: {
            'board': letters
        },
        success: function(data) { displayResults(data, board); }
    });
}

$(document).ready(function() {
    var board = new Board($('#GridTable'), initialGrid);
    if (board.isFilled())
    {
        solve(board.getLetters(), board);
    }

    $(document).bind('keypress', function(event) {

        if (!event.charCode)
            return;

        var boardWasFilled = board.isFilled();
        board.onLetter(String.fromCharCode(event.charCode));

        if (!boardWasFilled && board.isFilled())
            solve(board.getLetters(), board);
    });

    $(document).bind('keypress', function(event) {

        if (event.keyCode == 38 || event.keyCode == 40)
        {
            var goNext = (event.keyCode == 40);
            var next = $('.Result.Selected');
            next.removeClass('Selected');
            next = goNext ? next.next('.Result') : next.prev('.Result');
            if (next)
            {
                board.drawWord(next[0].xresult);
                next.addClass('Selected');
                event.preventDefault();
            }
        }

    });
});