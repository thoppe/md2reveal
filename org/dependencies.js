{ src: 'reveal.js/lib/js/classList.js', condition: function() { 
    return !document.body.classList; } },

{ src: 'reveal.js/plugin/markdown/showdown.js', condition: function() { 
    return !!document.querySelector( '[data-markdown]' ); } },

{ src: 'reveal.js/plugin/markdown/markdown.js', condition: function() { 
    return !!document.querySelector( '[data-markdown]' ); } },

{ src: 'reveal.js/plugin/highlight/highlight.js', async: true, callback: 
  function() { hljs.initHighlightingOnLoad(); } },

{ src: 'reveal.js/plugin/zoom-js/zoom.js', async: true, condition: 
  function() { return !!document.body.classList; } },
