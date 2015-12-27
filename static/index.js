function Board(parentElem)
{
    this._cells = parentElem.find('TD');
    console.log(this._cells.length);
    this._letters = '';
}

Board.prototype.onLetter = function(letter)
{
    if (this.isFilled())
        return;

    $(this._cells[this._letters.length]).text(letter);
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

function displayResults(results)
{
    var parentElem = $('#ResultsSection');
    for (var i = 0; i < results.length; i++)
    {
        parentElem.appendNewChild('DIV').text(results[i][0]);
    }
}

$(document).ready(function() {
    var board = new Board($('#GridTable'));

    $(document).bind('keypress', function(event) {

        var boardWasFilled = board.isFilled();
        board.onLetter(String.fromCharCode(event.charCode));

        if (!boardWasFilled && board.isFilled())
        {
            doAjax({
                url: '/solve/',
                method: 'POST',
                data: {
                    'board': board.getLetters()
                },
                success: displayResults
            });
        }
    });
});