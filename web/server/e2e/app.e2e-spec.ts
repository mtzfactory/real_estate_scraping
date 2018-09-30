import { ServerPage } from './app.po';

describe('server App', () => {
  let page: ServerPage;

  beforeEach(() => {
    page = new ServerPage();
  });

  it('should display welcome message', done => {
    page.navigateTo();
    page.getParagraphText()
      .then(msg => expect(msg).toEqual('Welcome to app!!'))
      .then(done, done.fail);
  });
});
