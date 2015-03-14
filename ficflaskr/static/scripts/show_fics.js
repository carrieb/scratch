var filters;

function setupFilterAutocomplete(user_id) {
  filters = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    limit: 10,
    prefetch: {
      url: '../data/saved_filters.json?user_id=' + user_id,
      filter: function(list) {
        return $.map(list, function(filter) { return { name: filter }; });
      } 
    }
  });

  filters.clearPrefetchCache()
  filters.initialize();

  $('#filter_auto').typeahead(null, {
    name: 'filters',
    highlight: true,
    displayKey: 'name',
    source: filters.ttAdapter()
  });
}

// Setup autocomplete for characters
var characters = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  limit: 10,
  prefetch: {
    url: '../data/characters.json',
    filter: function(list) {
      return $.map(list, function(character) { return { name: character }; });
    }
  }
});
 
characters.initialize();

$('#char_auto').tagsinput({
  tagClass: function(el) { return "label label-primary" },
  typeaheadjs: {
    name: 'characters',
    displayKey: 'name',
    valueKey: 'name',
    source: characters.ttAdapter()
  }
});

// Setup autocomplete for genres
var genres = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  limit: 10,
  prefetch: {
    url: '../data/genres.json',
    filter: function(list) {
      return $.map(list, function(genre) { return { name: genre }; });
    }
  }
});
 
genres.initialize();

// $('#genre_auto').typeahead(null, {
//   name: 'genres',
//   displayKey: 'name',
//   highlight: true,
//   source: genres.ttAdapter()
// });

$('#genre_auto').tagsinput({
  tagClass: function(el) { return "label label-danger" },
  typeaheadjs: {
    name: 'genres',
    displayKey: 'name',
    valueKey: 'name',
    source: genres.ttAdapter()
  }
});

// Setup autocomplete for pairings
var pairings = new Bloodhound({
  datumTokenizer: function(datum) { return Bloodhound.tokenizers.whitespace(datum.tokens.join(' ')); },
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  limit: 10,
  prefetch: {
    url: '../data/pairings.json',
    filter: function(list) {
      return $.map(list, function(pairing) { return { name: pairing, tokens: pairing.split('/') }; });
    }
  }
});
 
pairings.initialize();
 
// $('#pairing_auto').typeahead({highlight: true}, {
//   name: 'pairings',
//   displayKey: 'name',
//   // `ttAdapter` wraps the suggestion engine in an adapter that
//   // is compatible with the typeahead jQuery plugin
//   source: pairings.ttAdapter()
// });

$('#pairing_auto').tagsinput({
  tagClass: function(el) { return "label label-warning" },
  typeaheadjs: {
    name: 'pairings',
    displayKey: 'name',
    valueKey: 'name',
    source: pairings.ttAdapter()
  }
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

