r = window.r || {}

r.setup = function(config) {
    r.config = config
    // Set the legacy config global
    sciteit = config
}

$(function() {
    r.login.ui.init()
    r.analytics.init()
})
